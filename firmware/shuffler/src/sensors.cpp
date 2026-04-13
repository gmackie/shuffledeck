#include <Arduino.h>
#include "sensors.h"
#include "config.h"

// ============================================================
// ISR-shared state
// ============================================================

// Per-sensor volatile state
struct SensorISRState {
    volatile unsigned long last_fall_us;    // last beam-broken edge (falling)
    volatile unsigned long last_rise_us;    // last beam-cleared edge (rising)
    volatile bool event_pending;
    volatile unsigned long event_us;
    volatile uint16_t event_count;
    volatile unsigned long last_change_us;  // for stuck detection
};

static SensorISRState isr_state[NUM_SENSORS];

// Sensor pin lookup table
static const uint8_t sensor_pins[NUM_SENSORS] = {
    PIN_SENS_FEED_EXIT,
    PIN_SENS_POST_SING,
    PIN_SENS_SEL_THROAT,
    PIN_SENS_BIN_ENTRY,
    PIN_SENS_REC_PICKUP,
    PIN_SENS_OUTPUT,
};

// Map sensor index to CardEvent type (on beam-broken = card present)
static const CardEvent sensor_events[NUM_SENSORS] = {
    CardEvent::FEED_EXIT,
    CardEvent::POST_SINGULATE,
    CardEvent::SEL_TRANSIT,
    CardEvent::BIN_ENTRY,
    CardEvent::REC_PICKUP,
    CardEvent::OUTPUT_COUNT,
};

static const char* sensor_names[NUM_SENSORS] = {
    "feed_exit",
    "post_sing",
    "sel_throat",
    "bin_entry",
    "rec_pickup",
    "output",
};

// ============================================================
// ISR implementations — one per sensor
// Generic pattern: debounce, record edge, set event flag
// ============================================================

#define MAKE_ISR(IDX) \
static void IRAM_ATTR isr_sensor_##IDX() { \
    unsigned long now = micros(); \
    SensorISRState& s = isr_state[IDX]; \
    if (digitalRead(sensor_pins[IDX]) == LOW) { \
        if (now - s.last_fall_us > DEBOUNCE_US) { \
            s.last_fall_us = now; \
            s.event_us = now; \
            s.event_pending = true; \
            s.event_count++; \
            s.last_change_us = now; \
        } \
    } else { \
        if (now - s.last_rise_us > DEBOUNCE_US) { \
            s.last_rise_us = now; \
            s.last_change_us = now; \
        } \
    } \
}

MAKE_ISR(0)
MAKE_ISR(1)
MAKE_ISR(2)
MAKE_ISR(3)
MAKE_ISR(4)
MAKE_ISR(5)

// ISR function pointer table
static void (*isr_table[NUM_SENSORS])() = {
    isr_sensor_0,
    isr_sensor_1,
    isr_sensor_2,
    isr_sensor_3,
    isr_sensor_4,
    isr_sensor_5,
};

// ============================================================
// Public API
// ============================================================

void sensors_init() {
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        // GPIO 34-39 on ESP32 are input-only and have no internal pull-up.
        // External pull-ups required on those pins.
        if (sensor_pins[i] <= 33) {
            pinMode(sensor_pins[i], INPUT_PULLUP);
        } else {
            pinMode(sensor_pins[i], INPUT);
        }

        isr_state[i].last_fall_us = 0;
        isr_state[i].last_rise_us = 0;
        isr_state[i].event_pending = false;
        isr_state[i].event_us = 0;
        isr_state[i].event_count = 0;
        isr_state[i].last_change_us = micros();

        attachInterrupt(digitalPinToInterrupt(sensor_pins[i]),
                        isr_table[i], CHANGE);
    }
}

bool sensors_all_clear() {
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        if (digitalRead(sensor_pins[i]) == LOW) {
            return false;   // beam broken = something blocking
        }
    }
    return true;
}

bool sensor_is_blocked(uint8_t sensor_idx) {
    if (sensor_idx >= NUM_SENSORS) return false;
    return (digitalRead(sensor_pins[sensor_idx]) == LOW);
}

CardEvent sensors_poll_event() {
    // Priority order: feed_exit first (time-critical for counting)
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        if (isr_state[i].event_pending) {
            noInterrupts();
            isr_state[i].event_pending = false;
            interrupts();
            return sensor_events[i];
        }
    }
    return CardEvent::NONE;
}

unsigned long sensors_last_event_us() {
    // Return the most recent event timestamp across all sensors
    unsigned long latest = 0;
    noInterrupts();
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        if (isr_state[i].event_us > latest) {
            latest = isr_state[i].event_us;
        }
    }
    interrupts();
    return latest;
}

void sensors_reset() {
    noInterrupts();
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        isr_state[i].event_pending = false;
        isr_state[i].event_us = 0;
        isr_state[i].event_count = 0;
        isr_state[i].last_change_us = micros();
    }
    interrupts();
}

uint8_t sensors_raw_state() {
    uint8_t mask = 0;
    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        if (digitalRead(sensor_pins[i]) == LOW) {
            mask |= (1 << i);
        }
    }
    return mask;
}

const char* sensor_name(uint8_t idx) {
    if (idx >= NUM_SENSORS) return "unknown";
    return sensor_names[idx];
}

uint16_t sensor_event_count(uint8_t idx) {
    if (idx >= NUM_SENSORS) return 0;
    return isr_state[idx].event_count;
}

int8_t sensors_check_stuck(unsigned long timeout_ms) {
    unsigned long now = micros();
    unsigned long timeout_us = timeout_ms * 1000UL;

    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
        // Only flag as stuck if sensor is currently blocked AND
        // hasn't changed state in timeout period
        if (digitalRead(sensor_pins[i]) == LOW) {
            noInterrupts();
            unsigned long last_change = isr_state[i].last_change_us;
            interrupts();

            if ((now - last_change) > timeout_us) {
                return (int8_t)i;
            }
        }
    }
    return -1;
}
