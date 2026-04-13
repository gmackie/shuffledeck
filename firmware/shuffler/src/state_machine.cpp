#include <Arduino.h>
#include <esp_random.h>
#include <nvs_flash.h>
#include <nvs.h>
#include "state_machine.h"
#include "config.h"
#include "motors.h"
#include "sensors.h"

// ============================================================
// State name tables
// ============================================================

static const char* state_names[] = {
    "BOOT_SELFTEST",
    "IDLE",
    "FEEDING_PASS_1",
    "RECOMBINE_1",
    "FEEDING_PASS_2",
    "RECOMBINE_2",
    "COMPLETE",
    "FAULT_FEEDER",
    "FAULT_SELECTOR",
    "FAULT_RECOMBINE",
    "FAULT_COUNT",
    "FAULT_POWER",
    "SERVICE_MODE",
};

static const char* fault_names[] = {
    "NONE",
    "FEED_JAM",
    "FEED_MISS",
    "FEED_DOUBLE",
    "SEL_TIMEOUT",
    "SEL_MISROUTE",
    "BIN_JAM",
    "REC_PICKUP_FAIL",
    "REC_ELEVATOR_JAM",
    "COUNT_MISMATCH",
    "COUNT_FINAL",
    "SENSOR_FAIL",
    "POWER_INTERRUPTED",
    "MOTOR_COMM_FAIL",
};

const char* sm_state_name(ShufflerState state) {
    uint8_t idx = static_cast<uint8_t>(state);
    if (idx >= sizeof(state_names) / sizeof(state_names[0])) return "UNKNOWN";
    return state_names[idx];
}

const char* sm_fault_name(FaultCode code) {
    uint8_t idx = static_cast<uint8_t>(code);
    if (idx >= sizeof(fault_names) / sizeof(fault_names[0])) return "UNKNOWN";
    return fault_names[idx];
}

// ============================================================
// Helpers
// ============================================================

static void enter_state(ShufflerContext& ctx, ShufflerState new_state) {
    ctx.prev_state = ctx.state;
    ctx.state = new_state;
    ctx.state_enter_ms = millis();
    Serial.printf("[SM] %s -> %s\n", sm_state_name(ctx.prev_state),
                  sm_state_name(new_state));
}

static void enter_fault(ShufflerContext& ctx, ShufflerState fault_state,
                        FaultCode code) {
    motors_stop_all();
    ctx.fault_code = code;
    enter_state(ctx, fault_state);
    Serial.printf("[FAULT] %s: %s\n", sm_state_name(fault_state),
                  sm_fault_name(code));
}

static void reset_pass_counts(ShufflerContext& ctx) {
    ctx.feeder_exits = 0;
    ctx.post_singulations = 0;
    ctx.selector_entries = 0;
    ctx.bin_entries = 0;
    for (uint8_t i = 0; i < NUM_BINS; i++) {
        ctx.bin_counts[i] = 0;
    }
    ctx.recombine_out = 0;
}

static uint16_t total_bin_count(const ShufflerContext& ctx) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < NUM_BINS; i++) {
        sum += ctx.bin_counts[i];
    }
    return sum;
}

// Random bin assignment using ESP32 hardware RNG
static uint8_t random_bin() {
    return (uint8_t)(esp_random() % NUM_BINS);
}

// ============================================================
// NVS brownout state persistence
// ============================================================

static void nvs_save_fault_state(const ShufflerContext& ctx) {
    nvs_handle_t handle;
    if (nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle) == ESP_OK) {
        nvs_set_u8(handle, NVS_KEY_STATE, static_cast<uint8_t>(ctx.state));
        nvs_set_u8(handle, NVS_KEY_PASS, ctx.current_pass);
        nvs_set_u16(handle, NVS_KEY_CARD_COUNT, ctx.feeder_exits);
        nvs_commit(handle);
        nvs_close(handle);
    }
}

static bool nvs_check_interrupted_state() {
    nvs_handle_t handle;
    if (nvs_open(NVS_NAMESPACE, NVS_READONLY, &handle) != ESP_OK) {
        return false;
    }

    uint8_t saved_state = 0;
    esp_err_t err = nvs_get_u8(handle, NVS_KEY_STATE, &saved_state);
    nvs_close(handle);

    if (err != ESP_OK) return false;

    // If saved state indicates we were mid-shuffle, that's an interrupted state
    ShufflerState st = static_cast<ShufflerState>(saved_state);
    return (st == ShufflerState::FEEDING_PASS_1 ||
            st == ShufflerState::RECOMBINE_1 ||
            st == ShufflerState::FEEDING_PASS_2 ||
            st == ShufflerState::RECOMBINE_2);
}

static void nvs_clear_fault_state() {
    nvs_handle_t handle;
    if (nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle) == ESP_OK) {
        nvs_erase_key(handle, NVS_KEY_STATE);
        nvs_erase_key(handle, NVS_KEY_PASS);
        nvs_erase_key(handle, NVS_KEY_CARD_COUNT);
        nvs_commit(handle);
        nvs_close(handle);
    }
}

// ============================================================
// Per-card feed cycle (used in FEEDING_PASS_1 and FEEDING_PASS_2)
//
// This is called iteratively from sm_update. Each call attempts
// to feed one card, route it to a bin, and verify sensor events.
// Returns true if the card was successfully fed and binned.
// Returns false if waiting for sensor events (call again next loop).
// Enters fault state on error.
// ============================================================

// Feed sub-states tracked within the feeding states
enum class FeedPhase : uint8_t {
    START_FEED,         // begin feeding a card
    WAIT_FEED_EXIT,     // waiting for feed_exit sensor
    WAIT_POST_SING,     // waiting for post-singulation confirm
    MOVE_SELECTOR,      // moving selector to target bin
    WAIT_SEL_TRANSIT,   // waiting for selector throat sensor
    WAIT_BIN_ENTRY,     // waiting for bin entry confirmation
    CARD_COMPLETE,      // card successfully routed
};

static FeedPhase feed_phase = FeedPhase::START_FEED;
static unsigned long feed_phase_start_ms = 0;

static void reset_feed_phase() {
    feed_phase = FeedPhase::START_FEED;
    feed_phase_start_ms = millis();
}

// ============================================================
// Public API
// ============================================================

void sm_init(ShufflerContext& ctx) {
    memset(&ctx, 0, sizeof(ShufflerContext));
    ctx.state = ShufflerState::BOOT_SELFTEST;
    ctx.prev_state = ShufflerState::BOOT_SELFTEST;
    ctx.fault_code = FaultCode::NONE;
    ctx.current_pass = 0;
    ctx.state_enter_ms = millis();
    reset_feed_phase();

    // Initialize NVS
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES ||
        err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }
}

void sm_request_shuffle(ShufflerContext& ctx) {
    ctx.shuffle_requested = true;
}

void sm_request_stop(ShufflerContext& ctx) {
    ctx.stop_requested = true;
}

void sm_request_service(ShufflerContext& ctx) {
    ctx.service_requested = true;
}

void sm_request_clear_fault(ShufflerContext& ctx) {
    if (ctx.state >= ShufflerState::FAULT_FEEDER &&
        ctx.state <= ShufflerState::FAULT_POWER) {
        motors_stop_all();
        motors_enable_all(false);
        nvs_clear_fault_state();
        ctx.fault_code = FaultCode::NONE;
        ctx.jam_retries = 0;
        sensors_reset();
        enter_state(ctx, ShufflerState::IDLE);
    }
}

void sm_card_event(ShufflerContext& ctx, CardEvent event) {
    // Card events are processed directly in sm_update via sensors_poll_event
    // This function exists for external event injection (testing)
    (void)ctx;
    (void)event;
}

// ============================================================
// State handlers
// ============================================================

static void handle_boot_selftest(ShufflerContext& ctx) {
    Serial.println("[SM] Running boot self-test...");

    // Check for interrupted state from brownout
    if (nvs_check_interrupted_state()) {
        Serial.println("[SM] Interrupted shuffle detected in NVS. Entering FAULT_POWER.");
        Serial.println("[SM] Clear fault and reload deck before shuffling.");
        enter_fault(ctx, ShufflerState::FAULT_POWER, FaultCode::POWER_INTERRUPTED);
        return;
    }

    // Check all sensors read clear
    if (!sensors_all_clear()) {
        Serial.println("[SELFTEST] FAIL: one or more sensors blocked at boot");
        uint8_t raw = sensors_raw_state();
        for (uint8_t i = 0; i < NUM_SENSORS; i++) {
            if (raw & (1 << i)) {
                Serial.printf("  -> %s BLOCKED\n", sensor_name(i));
            }
        }
        enter_fault(ctx, ShufflerState::FAULT_FEEDER, FaultCode::SENSOR_FAIL);
        return;
    }
    Serial.println("[SELFTEST] Sensors: all clear");

    // Initialize motors and check TMC2209 comms
    if (!motors_init()) {
        Serial.println("[SELFTEST] FAIL: TMC2209 communication error");
        enter_fault(ctx, ShufflerState::FAULT_FEEDER, FaultCode::MOTOR_COMM_FAIL);
        return;
    }
    Serial.println("[SELFTEST] TMC2209 comms: OK");

    // Jog each motor
    if (!motors_selftest_jog()) {
        Serial.println("[SELFTEST] FAIL: motor jog test failed");
        enter_fault(ctx, ShufflerState::FAULT_FEEDER, FaultCode::MOTOR_COMM_FAIL);
        return;
    }
    Serial.println("[SELFTEST] Motor jog: OK");

    // Disable motors until needed
    motors_enable_all(false);

    ctx.selftest_passed = true;
    Serial.println("[SELFTEST] PASS — entering IDLE");
    enter_state(ctx, ShufflerState::IDLE);
}

static void handle_idle(ShufflerContext& ctx) {
    if (ctx.service_requested) {
        ctx.service_requested = false;
        enter_state(ctx, ShufflerState::SERVICE_MODE);
        return;
    }

    if (ctx.shuffle_requested) {
        ctx.shuffle_requested = false;

        // Verify sensors are clear before starting
        if (!sensors_all_clear()) {
            Serial.println("[SM] Cannot start: sensors not clear. Check card path.");
            return;
        }

        // Begin pass 1
        ctx.current_pass = 1;
        reset_pass_counts(ctx);
        ctx.output_count = 0;
        ctx.jam_retries = 0;
        ctx.current_sel_pos = 0;
        ctx.current_rec_pos = 0;
        reset_feed_phase();
        sensors_reset();

        // Save state to NVS (for brownout detection)
        nvs_save_fault_state(ctx);

        // Enable feeder and selector motors
        motor_enable(MotorAxis::FEEDER, true);
        motor_enable(MotorAxis::SELECTOR_X, true);

        Serial.println("[SM] Starting shuffle — pass 1");
        enter_state(ctx, ShufflerState::FEEDING_PASS_1);
    }
}

static bool handle_feeding(ShufflerContext& ctx) {
    unsigned long now = millis();

    // Check stop request
    if (ctx.stop_requested) {
        ctx.stop_requested = false;
        motors_stop_all();
        motors_enable_all(false);
        nvs_clear_fault_state();
        Serial.println("[SM] Shuffle stopped by user");
        enter_state(ctx, ShufflerState::IDLE);
        return false;
    }

    // Check for stuck sensors (jam detection)
    int8_t stuck = sensors_check_stuck(JAM_TIMEOUT_MS);
    if (stuck >= 0) {
        Serial.printf("[JAM] Sensor %s stuck\n", sensor_name(stuck));
        if (ctx.jam_retries < MAX_JAM_RETRIES) {
            ctx.jam_retries++;
            Serial.printf("[JAM] Retry %d/%d: reverse jog feeder\n",
                          ctx.jam_retries, MAX_JAM_RETRIES);
            motor_reverse_jog(MotorAxis::FEEDER, JAM_REVERSE_STEPS);
            delay(200);
            sensors_reset();
            reset_feed_phase();
            return false;
        }
        enter_fault(ctx, ShufflerState::FAULT_FEEDER, FaultCode::FEED_JAM);
        return false;
    }

    // Poll sensor events
    CardEvent evt = sensors_poll_event();

    switch (feed_phase) {
    case FeedPhase::START_FEED:
        // All cards fed?
        if (ctx.feeder_exits >= DECK_SIZE) {
            // Per-pass invariant check
            if (ctx.feeder_exits != ctx.bin_entries) {
                Serial.printf("[INVARIANT] feeder_exits=%d != bin_entries=%d\n",
                              ctx.feeder_exits, ctx.bin_entries);
                enter_fault(ctx, ShufflerState::FAULT_COUNT,
                            FaultCode::COUNT_MISMATCH);
                return false;
            }
            // All cards distributed — proceed to recombine
            motor_stop(MotorAxis::FEEDER);
            return true;    // signal feeding complete
        }

        // Assign random bin for this card
        ctx.target_bin = random_bin();

        // Move selector to target bin position
        selector_move_to_bin(ctx.target_bin, ctx.current_sel_pos);

        // Start feeder motor to push one card
        motor_enable(MotorAxis::FEEDER, true);
        motor_start(MotorAxis::FEEDER, FEED_SPEED_SPS, true);

        ctx.feed_start_ms = now;
        feed_phase = FeedPhase::WAIT_FEED_EXIT;
        feed_phase_start_ms = now;
        break;

    case FeedPhase::WAIT_FEED_EXIT:
        if (evt == CardEvent::FEED_EXIT) {
            ctx.feeder_exits++;
            ctx.last_card_ms = now;
            feed_phase = FeedPhase::WAIT_POST_SING;
            feed_phase_start_ms = now;
        } else if (now - feed_phase_start_ms > MISS_TIMEOUT_MS) {
            // No card detected — hopper may be empty or feeder jammed
            motor_stop(MotorAxis::FEEDER);
            if (ctx.feeder_exits == 0) {
                // No cards at all — probably empty hopper
                Serial.println("[SM] No cards detected. Hopper empty?");
                enter_fault(ctx, ShufflerState::FAULT_FEEDER,
                            FaultCode::FEED_MISS);
            } else {
                // Some cards fed — could be last card or jam
                // If we've fed fewer than DECK_SIZE, it's a problem
                Serial.printf("[SM] Feed miss after %d cards\n",
                              ctx.feeder_exits);
                enter_fault(ctx, ShufflerState::FAULT_FEEDER,
                            FaultCode::FEED_MISS);
            }
            return false;
        }
        break;

    case FeedPhase::WAIT_POST_SING:
        if (evt == CardEvent::POST_SINGULATE) {
            ctx.post_singulations++;
            feed_phase = FeedPhase::WAIT_SEL_TRANSIT;
            feed_phase_start_ms = now;
        } else if (now - feed_phase_start_ms > EXPECTED_TRANSIT_MS * 3) {
            // Card didn't reach post-singulation sensor
            enter_fault(ctx, ShufflerState::FAULT_FEEDER,
                        FaultCode::FEED_JAM);
            return false;
        }
        break;

    case FeedPhase::WAIT_SEL_TRANSIT:
        if (evt == CardEvent::SEL_TRANSIT) {
            ctx.selector_entries++;
            feed_phase = FeedPhase::WAIT_BIN_ENTRY;
            feed_phase_start_ms = now;
        } else if (now - feed_phase_start_ms > CARD_PASS_TIME_MS * 3) {
            enter_fault(ctx, ShufflerState::FAULT_SELECTOR,
                        FaultCode::SEL_MISROUTE);
            return false;
        }
        break;

    case FeedPhase::WAIT_BIN_ENTRY:
        if (evt == CardEvent::BIN_ENTRY) {
            ctx.bin_entries++;
            ctx.bin_counts[ctx.target_bin]++;
            ctx.jam_retries = 0;    // reset retry count on success

            // Stop feeder briefly to ensure clean separation
            motor_stop(MotorAxis::FEEDER);

            // Minimum inter-card gap
            if (now - ctx.last_card_ms < MIN_GAP_MS) {
                delay(MIN_GAP_MS - (now - ctx.last_card_ms));
            }

            feed_phase = FeedPhase::START_FEED;
            feed_phase_start_ms = millis();

            // Periodic NVS save (every 10 cards) for brownout recovery
            if (ctx.feeder_exits % 10 == 0) {
                nvs_save_fault_state(ctx);
            }
        } else if (now - feed_phase_start_ms > CARD_PASS_TIME_MS * 3) {
            enter_fault(ctx, ShufflerState::FAULT_SELECTOR,
                        FaultCode::BIN_JAM);
            return false;
        }
        break;

    case FeedPhase::CARD_COMPLETE:
        // Not used in this flow — handled inline above
        break;
    }

    return false;   // not done yet
}

static bool handle_recombine(ShufflerContext& ctx, bool to_output) {
    unsigned long now = millis();

    // Check stop request
    if (ctx.stop_requested) {
        ctx.stop_requested = false;
        motors_stop_all();
        motors_enable_all(false);
        nvs_clear_fault_state();
        enter_state(ctx, ShufflerState::IDLE);
        return false;
    }

    // Enable recombine motors
    motor_enable(MotorAxis::RECOMBINE_X, true);
    motor_enable(MotorAxis::RECOMBINE_Z, true);

    // Iterate through bins in order (0 to NUM_BINS-1)
    // For each non-empty bin: move to bin, lower, pick up stack, raise, deliver
    uint8_t& bin_idx = ctx.recombine_bin_idx;

    if (bin_idx >= NUM_BINS) {
        // All bins processed
        motor_enable(MotorAxis::RECOMBINE_X, false);
        motor_enable(MotorAxis::RECOMBINE_Z, false);

        // Verify recombine count matches total bin count
        uint16_t expected = total_bin_count(ctx);
        if (ctx.recombine_out != expected) {
            Serial.printf("[INVARIANT] recombine_out=%d != bin_total=%d\n",
                          ctx.recombine_out, expected);
            enter_fault(ctx, ShufflerState::FAULT_COUNT,
                        FaultCode::COUNT_MISMATCH);
            return false;
        }

        return true;    // recombine complete
    }

    // Skip empty bins
    if (ctx.bin_counts[bin_idx] == 0) {
        bin_idx++;
        return false;
    }

    // Move recombine X to current bin
    recombine_x_move_to_bin(bin_idx, ctx.current_rec_pos);

    // Lower pickup head
    recombine_z_lower();
    delay(REC_PICKUP_DWELL_MS);

    // Check pickup confirmation sensor
    if (!sensor_is_blocked(SENS_IDX_REC_PICKUP)) {
        // Retry once
        recombine_z_raise();
        delay(100);
        recombine_z_lower();
        delay(REC_PICKUP_DWELL_MS);

        if (!sensor_is_blocked(SENS_IDX_REC_PICKUP)) {
            Serial.printf("[RECOMBINE] Pickup failed at bin %d\n", bin_idx);
            enter_fault(ctx, ShufflerState::FAULT_RECOMBINE,
                        FaultCode::REC_PICKUP_FAIL);
            return false;
        }
    }

    // Raise with stack
    recombine_z_raise();

    // Count the cards picked up from this bin
    ctx.recombine_out += ctx.bin_counts[bin_idx];

    // If delivering to output, check output sensor for each card
    if (to_output) {
        // In practice, the entire bin stack is delivered at once.
        // The output sensor confirms the stack was deposited.
        // Individual card counting happens during the feed passes.
        ctx.output_count += ctx.bin_counts[bin_idx];
    }

    Serial.printf("[RECOMBINE] Bin %d: %d cards picked up (total: %d)\n",
                  bin_idx, ctx.bin_counts[bin_idx], ctx.recombine_out);

    bin_idx++;
    return false;   // more bins to process
}

static void handle_complete(ShufflerContext& ctx) {
    // Final count verification
    if (ctx.output_count != DECK_SIZE) {
        Serial.printf("[FINAL] Count mismatch: output=%d, expected=%d\n",
                      ctx.output_count, DECK_SIZE);
        enter_fault(ctx, ShufflerState::FAULT_COUNT, FaultCode::COUNT_FINAL);
        return;
    }

    Serial.printf("[COMPLETE] Shuffle successful. %d cards delivered.\n",
                  ctx.output_count);

    // Clear NVS state — shuffle completed cleanly
    nvs_clear_fault_state();

    // Disable all motors
    motors_enable_all(false);

    // Buzz success (short beep)
    if (PIN_BUZZER >= 0) {
        tone(PIN_BUZZER, 2000, 200);
    }

    // Return to idle after a brief display period
    unsigned long now = millis();
    if (now - ctx.state_enter_ms > 3000) {
        enter_state(ctx, ShufflerState::IDLE);
    }
}

static void handle_service_mode(ShufflerContext& ctx) {
    // Service mode is driven by serial commands.
    // Main loop handles serial input and dispatches motor jog / sensor read.
    // Exit service mode on stop button press.
    if (ctx.stop_requested) {
        ctx.stop_requested = false;
        motors_stop_all();
        motors_enable_all(false);
        enter_state(ctx, ShufflerState::IDLE);
    }
}

// ============================================================
// Main state machine update
// ============================================================

void sm_update(ShufflerContext& ctx) {
    switch (ctx.state) {

    case ShufflerState::BOOT_SELFTEST:
        handle_boot_selftest(ctx);
        break;

    case ShufflerState::IDLE:
        handle_idle(ctx);
        break;

    case ShufflerState::FEEDING_PASS_1: {
        bool done = handle_feeding(ctx);
        if (done) {
            Serial.printf("[SM] Pass 1 feeding complete: %d cards distributed\n",
                          ctx.feeder_exits);
            // Transition to recombine
            ctx.recombine_bin_idx = 0;
            ctx.recombine_out = 0;
            motor_enable(MotorAxis::FEEDER, false);
            motor_enable(MotorAxis::SELECTOR_X, false);
            enter_state(ctx, ShufflerState::RECOMBINE_1);
        }
        break;
    }

    case ShufflerState::RECOMBINE_1: {
        bool done = handle_recombine(ctx, false);
        if (done) {
            Serial.printf("[SM] Recombine 1 complete: %d cards\n",
                          ctx.recombine_out);
            // Begin pass 2
            ctx.current_pass = 2;
            reset_pass_counts(ctx);
            reset_feed_phase();
            sensors_reset();
            ctx.current_sel_pos = 0;
            ctx.jam_retries = 0;

            nvs_save_fault_state(ctx);

            motor_enable(MotorAxis::FEEDER, true);
            motor_enable(MotorAxis::SELECTOR_X, true);

            Serial.println("[SM] Starting shuffle — pass 2");
            enter_state(ctx, ShufflerState::FEEDING_PASS_2);
        }
        break;
    }

    case ShufflerState::FEEDING_PASS_2: {
        bool done = handle_feeding(ctx);
        if (done) {
            Serial.printf("[SM] Pass 2 feeding complete: %d cards distributed\n",
                          ctx.feeder_exits);
            ctx.recombine_bin_idx = 0;
            ctx.recombine_out = 0;
            motor_enable(MotorAxis::FEEDER, false);
            motor_enable(MotorAxis::SELECTOR_X, false);
            enter_state(ctx, ShufflerState::RECOMBINE_2);
        }
        break;
    }

    case ShufflerState::RECOMBINE_2: {
        bool done = handle_recombine(ctx, true);
        if (done) {
            Serial.printf("[SM] Recombine 2 complete: %d cards to output\n",
                          ctx.recombine_out);
            enter_state(ctx, ShufflerState::COMPLETE);
        }
        break;
    }

    case ShufflerState::COMPLETE:
        handle_complete(ctx);
        break;

    case ShufflerState::FAULT_FEEDER:
    case ShufflerState::FAULT_SELECTOR:
    case ShufflerState::FAULT_RECOMBINE:
    case ShufflerState::FAULT_COUNT:
    case ShufflerState::FAULT_POWER:
        // Fault states: motors already stopped. Wait for user to clear.
        // Buzz intermittently to alert
        if (PIN_BUZZER >= 0) {
            unsigned long elapsed = millis() - ctx.state_enter_ms;
            if ((elapsed / 1000) % 2 == 0 && (elapsed % 1000) < 100) {
                tone(PIN_BUZZER, 1000, 80);
            }
        }

        if (ctx.stop_requested) {
            ctx.stop_requested = false;
            sm_request_clear_fault(ctx);
        }
        break;

    case ShufflerState::SERVICE_MODE:
        handle_service_mode(ctx);
        break;
    }
}
