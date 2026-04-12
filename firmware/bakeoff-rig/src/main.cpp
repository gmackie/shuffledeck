// Feeder singulation bakeoff rig — ESP32 firmware
// Counts and classifies cards exiting a feeder under test.
// Serial CSV output for host-side capture.

#include <Arduino.h>
#include "config.h"

// ----------------------------------------------------------
// ISR-shared state (volatile)
// ----------------------------------------------------------

static volatile unsigned long s1_rise_us = 0;  // last sensor1 falling edge (beam broken)
static volatile unsigned long s1_fall_us = 0;  // last sensor1 rising edge (beam cleared)
static volatile unsigned long s2_rise_us = 0;
static volatile unsigned long s2_fall_us = 0;

// Edge timestamps latched for main loop consumption.
// ISR sets the flag; main loop clears it after processing.
static volatile bool s1_event = false;
static volatile bool s2_event = false;
static volatile unsigned long s1_event_us = 0;
static volatile unsigned long s2_event_us = 0;

// ----------------------------------------------------------
// ISRs — record edge timestamps
// ----------------------------------------------------------

static void IRAM_ATTR isr_sensor1() {
    unsigned long now = micros();
    // Debounce
    if (digitalRead(PIN_SENSOR1) == LOW) {
        // Falling edge: beam broken (card arrived)
        if (now - s1_rise_us > DEBOUNCE_US) {
            s1_rise_us = now;
            s1_event_us = now;
            s1_event = true;
        }
    } else {
        // Rising edge: beam cleared (card passed)
        if (now - s1_fall_us > DEBOUNCE_US) {
            s1_fall_us = now;
        }
    }
}

static void IRAM_ATTR isr_sensor2() {
    unsigned long now = micros();
    if (digitalRead(PIN_SENSOR2) == LOW) {
        if (now - s2_rise_us > DEBOUNCE_US) {
            s2_rise_us = now;
            s2_event_us = now;
            s2_event = true;
        }
    } else {
        if (now - s2_fall_us > DEBOUNCE_US) {
            s2_fall_us = now;
        }
    }
}

// ----------------------------------------------------------
// State
// ----------------------------------------------------------

enum RigState { IDLE, RUNNING };
static RigState state = IDLE;

static uint32_t event_id = 0;
static uint32_t stat_total = 0;
static uint32_t stat_singles = 0;
static uint32_t stat_doubles = 0;
static uint32_t stat_misses = 0;
static uint32_t stat_skews = 0;
static uint32_t stat_jams = 0;

// Pending event tracking
static bool waiting_for_s2 = false;      // sensor1 fired, waiting for sensor2
static unsigned long pending_s1_ms = 0;  // millis() when sensor1 fired
static unsigned long pending_s1_us = 0;  // micros() when sensor1 fired

static unsigned long last_card_time_ms = 0;  // millis() of last completed event
static unsigned long run_start_ms = 0;

// Button debounce
static unsigned long last_button_ms = 0;

// ----------------------------------------------------------
// Helpers
// ----------------------------------------------------------

static void emit_csv(unsigned long t_ms, unsigned long s1_edge_ms,
                     unsigned long s2_edge_ms, const char* classification,
                     long transit_ms, const char* notes) {
    event_id++;
    Serial.printf("%u,%lu,%lu,%lu,%s,%ld,%s\n",
                  event_id, t_ms, s1_edge_ms, s2_edge_ms,
                  classification, transit_ms, notes ? notes : "");
}

static void print_stats() {
    Serial.println("# --- stats ---");
    Serial.printf("# total=%u singles=%u doubles=%u misses=%u skews=%u jams=%u\n",
                  stat_total, stat_singles, stat_doubles, stat_misses,
                  stat_skews, stat_jams);
    Serial.println("# -------------");
}

static void reset_stats() {
    event_id = 0;
    stat_total = 0;
    stat_singles = 0;
    stat_doubles = 0;
    stat_misses = 0;
    stat_skews = 0;
    stat_jams = 0;
    waiting_for_s2 = false;
}

// ----------------------------------------------------------
// Setup
// ----------------------------------------------------------

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    pinMode(PIN_SENSOR1, INPUT_PULLUP);
    pinMode(PIN_SENSOR2, INPUT_PULLUP);
    pinMode(PIN_BUTTON, INPUT_PULLUP);

    if (PIN_MOTOR >= 0) {
        pinMode(PIN_MOTOR, OUTPUT);
        digitalWrite(PIN_MOTOR, LOW);
    }

    attachInterrupt(digitalPinToInterrupt(PIN_SENSOR1), isr_sensor1, CHANGE);
    attachInterrupt(digitalPinToInterrupt(PIN_SENSOR2), isr_sensor2, CHANGE);

    Serial.println("# feeder-bakeoff-rig v1.0");
    Serial.printf("# feed_speed=%.0f mm/s  sensor_spacing=%.0f mm  card_length=%.0f mm\n",
                  FEED_SPEED_MMS, SENSOR_SPACING_MM, CARD_LENGTH_MM);
    Serial.printf("# expected_transit=%lu ms  double_thresh=%lu ms  jam_timeout=%lu ms  miss_timeout=%lu ms\n",
                  EXPECTED_TRANSIT_MS, DOUBLE_THRESHOLD_MS, JAM_TIMEOUT_MS, MISS_TIMEOUT_MS);
    Serial.println("# press button to start/stop");
    Serial.println("event_id,t_ms,sensor1_edge,sensor2_edge,classification,transit_ms,notes");
}

// ----------------------------------------------------------
// Main loop
// ----------------------------------------------------------

void loop() {
    unsigned long now_ms = millis();

    // ---- Button handling (toggle start/stop) ----
    if (digitalRead(PIN_BUTTON) == LOW && (now_ms - last_button_ms > 300)) {
        last_button_ms = now_ms;
        if (state == IDLE) {
            state = RUNNING;
            reset_stats();
            run_start_ms = now_ms;
            last_card_time_ms = now_ms;
            Serial.println("# RUN START");
            if (PIN_MOTOR >= 0) digitalWrite(PIN_MOTOR, HIGH);
        } else {
            state = IDLE;
            if (PIN_MOTOR >= 0) digitalWrite(PIN_MOTOR, LOW);
            Serial.println("# RUN STOP");
            print_stats();
        }
    }

    if (state != RUNNING) return;

    // ---- Process sensor1 event ----
    if (s1_event) {
        noInterrupts();
        unsigned long ts = s1_event_us;
        s1_event = false;
        interrupts();

        unsigned long ts_ms = ts / 1000;

        if (!waiting_for_s2) {
            waiting_for_s2 = true;
            pending_s1_ms = now_ms;
            pending_s1_us = ts;
        }
        // If already waiting, a second s1 trigger before s2 is unusual;
        // ignore (debounce should handle it).
    }

    // ---- Process sensor2 event (completes a card event) ----
    if (s2_event && waiting_for_s2) {
        noInterrupts();
        unsigned long ts = s2_event_us;
        s2_event = false;
        interrupts();

        unsigned long s1_ms = pending_s1_us / 1000;
        unsigned long s2_ms = ts / 1000;
        long transit = (long)(s2_ms - s1_ms);

        waiting_for_s2 = false;
        stat_total++;

        // Check if both sensors are currently blocked (double detection)
        bool s1_blocked = (digitalRead(PIN_SENSOR1) == LOW);
        bool s2_blocked = (digitalRead(PIN_SENSOR2) == LOW);

        if (transit <= 0 || (s1_blocked && s2_blocked &&
            (unsigned long)transit > DOUBLE_THRESHOLD_MS)) {
            // Double: simultaneous block or overlap too long
            stat_doubles++;
            emit_csv(now_ms - run_start_ms, s1_ms, s2_ms, "double", transit,
                     transit <= 0 ? "simultaneous_block" : "extended_overlap");
        } else {
            // Check skew
            long expected = (long)EXPECTED_TRANSIT_MS;
            long deviation = abs(transit - expected);
            float ratio = (float)deviation / (float)expected;

            if (ratio > SKEW_TOLERANCE) {
                stat_skews++;
                emit_csv(now_ms - run_start_ms, s1_ms, s2_ms, "skew", transit, "");
            } else {
                stat_singles++;
                emit_csv(now_ms - run_start_ms, s1_ms, s2_ms, "single", transit, "");
            }
        }

        last_card_time_ms = now_ms;

    } else if (s2_event && !waiting_for_s2) {
        // Spurious s2 without s1 — ignore but clear flag
        noInterrupts();
        s2_event = false;
        interrupts();
    }

    // ---- Jam detection: sensor blocked too long ----
    if (waiting_for_s2 && (now_ms - pending_s1_ms > JAM_TIMEOUT_MS)) {
        stat_total++;
        stat_jams++;
        unsigned long s1_ms = pending_s1_us / 1000;
        emit_csv(now_ms - run_start_ms, s1_ms, 0, "jam", 0, "sensor_blocked_timeout");
        waiting_for_s2 = false;
        last_card_time_ms = now_ms;

        // Stop motor on jam — operator must clear and restart
        if (PIN_MOTOR >= 0) digitalWrite(PIN_MOTOR, LOW);
        state = IDLE;
        Serial.println("# JAM DETECTED — motor stopped. Clear and restart.");
        print_stats();
    }

    // ---- Miss detection: no sensor trigger for too long ----
    if (!waiting_for_s2 && (now_ms - last_card_time_ms > MISS_TIMEOUT_MS)) {
        stat_total++;
        stat_misses++;
        emit_csv(now_ms - run_start_ms, 0, 0, "miss", 0, "no_trigger_timeout");
        last_card_time_ms = now_ms;  // reset timer to avoid repeated misses
    }
}
