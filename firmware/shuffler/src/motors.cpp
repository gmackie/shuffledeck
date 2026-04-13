#include <Arduino.h>
#include <TMCStepper.h>
#include "motors.h"
#include "config.h"

// ============================================================
// TMC2209 driver instances (shared UART bus, addressed 0-3)
// ============================================================

static TMC2209Stepper tmc_feed(PIN_TMC_RX, PIN_TMC_TX, TMC_R_SENSE, FEED_TMC_ADDR);
static TMC2209Stepper tmc_sel(PIN_TMC_RX, PIN_TMC_TX, TMC_R_SENSE, SEL_TMC_ADDR);
static TMC2209Stepper tmc_rec_x(PIN_TMC_RX, PIN_TMC_TX, TMC_R_SENSE, REC_X_TMC_ADDR);
static TMC2209Stepper tmc_rec_z(PIN_TMC_RX, PIN_TMC_TX, TMC_R_SENSE, REC_Z_TMC_ADDR);

// ============================================================
// Per-axis runtime state
// ============================================================

struct AxisState {
    uint8_t pin_step;
    uint8_t pin_dir;
    uint8_t pin_en;
    TMC2209Stepper* driver;
    uint32_t speed_sps;         // configured speed
    uint16_t current_ma;        // configured current

    // Non-blocking move state
    volatile int32_t steps_remaining;
    volatile bool direction;    // true = forward
    volatile bool running;
    unsigned long step_interval_us;
    unsigned long last_step_us;
};

static AxisState axes[4];

// ============================================================
// Initialization
// ============================================================

static void init_axis(AxisState& ax, uint8_t step, uint8_t dir, uint8_t en,
                      TMC2209Stepper* drv, uint32_t speed, uint16_t current) {
    ax.pin_step = step;
    ax.pin_dir = dir;
    ax.pin_en = en;
    ax.driver = drv;
    ax.speed_sps = speed;
    ax.current_ma = current;
    ax.steps_remaining = 0;
    ax.direction = true;
    ax.running = false;
    ax.step_interval_us = 1000000UL / speed;
    ax.last_step_us = 0;

    pinMode(step, OUTPUT);
    pinMode(dir, OUTPUT);
    pinMode(en, OUTPUT);
    digitalWrite(en, HIGH);     // HIGH = disabled for TMC2209
    digitalWrite(step, LOW);
    digitalWrite(dir, LOW);
}

static bool init_tmc(TMC2209Stepper& drv, uint16_t current_ma) {
    drv.begin();
    drv.toff(4);                // enable driver (toff > 0)
    drv.blank_time(24);
    drv.rms_current(current_ma);
    drv.microsteps(16);
    drv.pwm_autoscale(true);    // StealthChop
    drv.en_spreadCycle(false);
    drv.TCOOLTHRS(0xFFFFF);     // enable StallGuard at all speeds
    drv.semin(5);               // CoolStep minimum
    drv.semax(2);               // CoolStep maximum

    // Verify communication by reading version register
    uint8_t ver = drv.version();
    return (ver == 0x21);       // TMC2209 version = 0x21
}

bool motors_init() {
    // Initialize axis state
    init_axis(axes[0], PIN_FEED_STEP, PIN_FEED_DIR, PIN_FEED_EN,
              &tmc_feed, FEED_SPEED_SPS, FEED_CURRENT_MA);
    init_axis(axes[1], PIN_SEL_STEP, PIN_SEL_DIR, PIN_SEL_EN,
              &tmc_sel, SEL_SPEED_SPS, SEL_CURRENT_MA);
    init_axis(axes[2], PIN_REC_X_STEP, PIN_REC_X_DIR, PIN_REC_X_EN,
              &tmc_rec_x, REC_X_SPEED_SPS, REC_X_CURRENT_MA);
    init_axis(axes[3], PIN_REC_Z_STEP, PIN_REC_Z_DIR, PIN_REC_Z_EN,
              &tmc_rec_z, REC_Z_SPEED_SPS, REC_Z_CURRENT_MA);

    // Initialize UART and configure each TMC2209
    bool all_ok = true;
    all_ok &= init_tmc(tmc_feed, FEED_CURRENT_MA);
    all_ok &= init_tmc(tmc_sel, SEL_CURRENT_MA);
    all_ok &= init_tmc(tmc_rec_x, REC_X_CURRENT_MA);
    all_ok &= init_tmc(tmc_rec_z, REC_Z_CURRENT_MA);

    return all_ok;
}

// ============================================================
// Enable / Disable
// ============================================================

void motor_enable(MotorAxis axis, bool enabled) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return;
    // TMC2209: LOW = enabled, HIGH = disabled
    digitalWrite(axes[idx].pin_en, enabled ? LOW : HIGH);
}

void motors_enable_all(bool enabled) {
    for (uint8_t i = 0; i < 4; i++) {
        digitalWrite(axes[i].pin_en, enabled ? LOW : HIGH);
    }
}

// ============================================================
// Blocking move
// ============================================================

void motor_move(MotorAxis axis, int32_t steps, bool dir) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4 || steps <= 0) return;

    AxisState& ax = axes[idx];
    digitalWrite(ax.pin_dir, dir ? HIGH : LOW);

    unsigned long interval = ax.step_interval_us;

    for (int32_t i = 0; i < steps; i++) {
        digitalWrite(ax.pin_step, HIGH);
        delayMicroseconds(2);           // minimum pulse width
        digitalWrite(ax.pin_step, LOW);
        delayMicroseconds(interval > 2 ? interval - 2 : 1);
    }
}

// ============================================================
// Non-blocking move
// ============================================================

void motor_start(MotorAxis axis, uint32_t speed_sps, bool dir) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return;

    AxisState& ax = axes[idx];
    ax.step_interval_us = 1000000UL / speed_sps;
    ax.direction = dir;
    ax.steps_remaining = INT32_MAX;     // run until stopped
    ax.running = true;
    ax.last_step_us = micros();
    digitalWrite(ax.pin_dir, dir ? HIGH : LOW);
}

void motor_stop(MotorAxis axis) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return;
    axes[idx].steps_remaining = 0;
    axes[idx].running = false;
}

void motors_stop_all() {
    for (uint8_t i = 0; i < 4; i++) {
        axes[i].steps_remaining = 0;
        axes[i].running = false;
    }
}

bool motor_is_moving(MotorAxis axis) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return false;
    return axes[idx].running;
}

void motors_run() {
    unsigned long now = micros();

    for (uint8_t i = 0; i < 4; i++) {
        AxisState& ax = axes[i];
        if (!ax.running || ax.steps_remaining <= 0) continue;

        if ((now - ax.last_step_us) >= ax.step_interval_us) {
            digitalWrite(ax.pin_step, HIGH);
            delayMicroseconds(2);
            digitalWrite(ax.pin_step, LOW);
            ax.last_step_us = now;
            ax.steps_remaining--;

            if (ax.steps_remaining <= 0) {
                ax.running = false;
            }
        }
    }
}

// ============================================================
// High-level motion commands
// ============================================================

void selector_move_to_bin(uint8_t bin, uint8_t& current_pos) {
    if (bin >= NUM_BINS) return;
    int16_t delta = (int16_t)bin - (int16_t)current_pos;
    if (delta == 0) return;

    bool dir = (delta > 0);
    int32_t steps = abs(delta) * SEL_STEPS_PER_BIN;
    motor_enable(MotorAxis::SELECTOR_X, true);
    motor_move(MotorAxis::SELECTOR_X, steps, dir);
    current_pos = bin;
    delay(SEL_SETTLE_MS);
}

void recombine_x_move_to_bin(uint8_t bin, uint8_t& current_pos) {
    if (bin >= NUM_BINS) return;
    int16_t delta = (int16_t)bin - (int16_t)current_pos;
    if (delta == 0) return;

    bool dir = (delta > 0);
    int32_t steps = abs(delta) * REC_X_STEPS_PER_BIN;
    motor_enable(MotorAxis::RECOMBINE_X, true);
    motor_move(MotorAxis::RECOMBINE_X, steps, dir);
    current_pos = bin;
    delay(SEL_SETTLE_MS);
}

void recombine_z_lower() {
    motor_enable(MotorAxis::RECOMBINE_Z, true);
    motor_move(MotorAxis::RECOMBINE_Z, REC_Z_STEPS_DOWN, true);
}

void recombine_z_raise() {
    motor_enable(MotorAxis::RECOMBINE_Z, true);
    motor_move(MotorAxis::RECOMBINE_Z, REC_Z_STEPS_UP, false);
}

// ============================================================
// Self-test and diagnostics
// ============================================================

bool motors_selftest_jog() {
    bool ok = true;

    for (uint8_t i = 0; i < 4; i++) {
        MotorAxis axis = static_cast<MotorAxis>(i);
        motor_enable(axis, true);
        delay(10);

        // Jog forward
        motor_move(axis, SELFTEST_JOG_STEPS, true);
        delay(50);

        // Jog back
        motor_move(axis, SELFTEST_JOG_STEPS, false);
        delay(50);

        // Check driver communication
        if (!motor_check_comm(axis)) {
            ok = false;
        }

        motor_enable(axis, false);
    }

    return ok;
}

void motor_reverse_jog(MotorAxis axis, int32_t steps) {
    motor_enable(axis, true);
    motor_move(axis, steps, false);     // reverse direction
}

bool motor_check_comm(MotorAxis axis) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return false;
    uint8_t ver = axes[idx].driver->version();
    return (ver == 0x21);
}

uint32_t motor_get_status(MotorAxis axis) {
    uint8_t idx = static_cast<uint8_t>(axis);
    if (idx >= 4) return 0;
    return axes[idx].driver->DRV_STATUS();
}
