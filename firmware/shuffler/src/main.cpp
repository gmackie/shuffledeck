// Single-deck automatic card shuffler — production firmware
// ESP32 + TMC2209 UART stepper drivers
// Two-pass 8-bin random shuffle with per-pass count invariants

#include <Arduino.h>
#include <Wire.h>
#include <SSD1306Wire.h>
#include "config.h"
#include "state_machine.h"
#include "motors.h"
#include "sensors.h"

// ============================================================
// Globals
// ============================================================

static ShufflerContext ctx;
static SSD1306Wire display(OLED_ADDR, PIN_OLED_SDA, PIN_OLED_SCL);

// Button debounce state
static unsigned long last_shuffle_btn_ms = 0;
static unsigned long last_stop_btn_ms = 0;

// Display update rate limiting
static unsigned long last_display_ms = 0;
static const unsigned long DISPLAY_INTERVAL_MS = 100;

// Serial command buffer for service mode
static char cmd_buf[32];
static uint8_t cmd_len = 0;

// ============================================================
// OLED display helpers
// ============================================================

static void display_init() {
    display.init();
    display.flipScreenVertically();
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.clear();
    display.drawString(0, 0, "Card Shuffler V1");
    display.drawString(0, 16, "Booting...");
    display.display();
}

static void display_update() {
    unsigned long now = millis();
    if (now - last_display_ms < DISPLAY_INTERVAL_MS) return;
    last_display_ms = now;

    display.clear();

    // Line 0: state
    display.setFont(ArialMT_Plain_10);
    display.drawString(0, 0, sm_state_name(ctx.state));

    switch (ctx.state) {
    case ShufflerState::IDLE:
        display.setFont(ArialMT_Plain_16);
        display.drawString(0, 20, "Ready");
        display.setFont(ArialMT_Plain_10);
        display.drawString(0, 42, "Press SHUFFLE to start");
        break;

    case ShufflerState::FEEDING_PASS_1:
    case ShufflerState::FEEDING_PASS_2: {
        char line1[32], line2[32], line3[32];
        snprintf(line1, sizeof(line1), "Pass %d  Card %d/%d",
                 ctx.current_pass, ctx.feeder_exits, DECK_SIZE);
        snprintf(line2, sizeof(line2), "Bins: %d %d %d %d",
                 ctx.bin_counts[0], ctx.bin_counts[1],
                 ctx.bin_counts[2], ctx.bin_counts[3]);
        snprintf(line3, sizeof(line3), "      %d %d %d %d",
                 ctx.bin_counts[4], ctx.bin_counts[5],
                 ctx.bin_counts[6], ctx.bin_counts[7]);
        display.drawString(0, 14, line1);
        display.drawString(0, 28, line2);
        display.drawString(0, 42, line3);
        break;
    }

    case ShufflerState::RECOMBINE_1:
    case ShufflerState::RECOMBINE_2: {
        char line1[32], line2[32];
        snprintf(line1, sizeof(line1), "Recombine %d",
                 ctx.state == ShufflerState::RECOMBINE_1 ? 1 : 2);
        snprintf(line2, sizeof(line2), "Bin %d/%d  Cards %d",
                 ctx.recombine_bin_idx, NUM_BINS, ctx.recombine_out);
        display.drawString(0, 14, line1);
        display.drawString(0, 28, line2);
        break;
    }

    case ShufflerState::COMPLETE: {
        display.setFont(ArialMT_Plain_16);
        display.drawString(0, 16, "Done!");
        display.setFont(ArialMT_Plain_10);
        char line[32];
        snprintf(line, sizeof(line), "%d cards shuffled", ctx.output_count);
        display.drawString(0, 38, line);
        break;
    }

    case ShufflerState::FAULT_FEEDER:
    case ShufflerState::FAULT_SELECTOR:
    case ShufflerState::FAULT_RECOMBINE:
    case ShufflerState::FAULT_COUNT:
    case ShufflerState::FAULT_POWER: {
        display.setFont(ArialMT_Plain_16);
        display.drawString(0, 14, "FAULT");
        display.setFont(ArialMT_Plain_10);
        display.drawString(0, 34, sm_fault_name(ctx.fault_code));
        display.drawString(0, 48, "Press STOP to clear");
        break;
    }

    case ShufflerState::SERVICE_MODE: {
        display.drawString(0, 14, "Service Mode");
        char raw_line[32];
        uint8_t raw = sensors_raw_state();
        snprintf(raw_line, sizeof(raw_line), "Sensors: 0x%02X", raw);
        display.drawString(0, 28, raw_line);

        // Show individual sensor states
        char sens_line[48];
        snprintf(sens_line, sizeof(sens_line), "%c%c%c%c%c%c",
                 (raw & 0x01) ? 'F' : '.', (raw & 0x02) ? 'S' : '.',
                 (raw & 0x04) ? 'T' : '.', (raw & 0x08) ? 'B' : '.',
                 (raw & 0x10) ? 'R' : '.', (raw & 0x20) ? 'O' : '.');
        display.drawString(0, 42, sens_line);
        display.drawString(42, 42, " FdSnThBnRcOu");
        break;
    }

    case ShufflerState::BOOT_SELFTEST:
        display.drawString(0, 14, "Self-test...");
        break;
    }

    display.display();
}

// ============================================================
// Button handling
// ============================================================

static void handle_buttons() {
    unsigned long now = millis();

    // Shuffle button
    if (digitalRead(PIN_BTN_SHUFFLE) == LOW &&
        (now - last_shuffle_btn_ms > BTN_DEBOUNCE_MS)) {
        last_shuffle_btn_ms = now;

        if (ctx.state == ShufflerState::IDLE) {
            sm_request_shuffle(ctx);
        } else if (ctx.state == ShufflerState::SERVICE_MODE) {
            // In service mode, shuffle button exits
            sm_request_stop(ctx);
        }
    }

    // Stop button
    if (digitalRead(PIN_BTN_STOP) == LOW &&
        (now - last_stop_btn_ms > BTN_DEBOUNCE_MS)) {
        last_stop_btn_ms = now;

        if (ctx.state == ShufflerState::IDLE) {
            // Long-press stop in idle enters service mode
            // (Simple: just single press for now)
            sm_request_service(ctx);
        } else {
            sm_request_stop(ctx);
        }
    }
}

// ============================================================
// Serial command handler (service mode)
// ============================================================

static void handle_serial_commands() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (cmd_len == 0) continue;
            cmd_buf[cmd_len] = '\0';

            // Parse command
            if (ctx.state == ShufflerState::SERVICE_MODE) {
                if (strcmp(cmd_buf, "jog feed+") == 0) {
                    motor_enable(MotorAxis::FEEDER, true);
                    motor_move(MotorAxis::FEEDER, 200, true);
                    motor_enable(MotorAxis::FEEDER, false);
                    Serial.println("OK jog feed+");
                } else if (strcmp(cmd_buf, "jog feed-") == 0) {
                    motor_enable(MotorAxis::FEEDER, true);
                    motor_move(MotorAxis::FEEDER, 200, false);
                    motor_enable(MotorAxis::FEEDER, false);
                    Serial.println("OK jog feed-");
                } else if (strcmp(cmd_buf, "jog sel+") == 0) {
                    motor_enable(MotorAxis::SELECTOR_X, true);
                    motor_move(MotorAxis::SELECTOR_X, SEL_STEPS_PER_BIN, true);
                    motor_enable(MotorAxis::SELECTOR_X, false);
                    Serial.println("OK jog sel+");
                } else if (strcmp(cmd_buf, "jog sel-") == 0) {
                    motor_enable(MotorAxis::SELECTOR_X, true);
                    motor_move(MotorAxis::SELECTOR_X, SEL_STEPS_PER_BIN, false);
                    motor_enable(MotorAxis::SELECTOR_X, false);
                    Serial.println("OK jog sel-");
                } else if (strcmp(cmd_buf, "jog recx+") == 0) {
                    motor_enable(MotorAxis::RECOMBINE_X, true);
                    motor_move(MotorAxis::RECOMBINE_X, REC_X_STEPS_PER_BIN, true);
                    motor_enable(MotorAxis::RECOMBINE_X, false);
                    Serial.println("OK jog recx+");
                } else if (strcmp(cmd_buf, "jog recx-") == 0) {
                    motor_enable(MotorAxis::RECOMBINE_X, true);
                    motor_move(MotorAxis::RECOMBINE_X, REC_X_STEPS_PER_BIN, false);
                    motor_enable(MotorAxis::RECOMBINE_X, false);
                    Serial.println("OK jog recx-");
                } else if (strcmp(cmd_buf, "jog recz+") == 0) {
                    motor_enable(MotorAxis::RECOMBINE_Z, true);
                    motor_move(MotorAxis::RECOMBINE_Z, 200, true);
                    motor_enable(MotorAxis::RECOMBINE_Z, false);
                    Serial.println("OK jog recz+");
                } else if (strcmp(cmd_buf, "jog recz-") == 0) {
                    motor_enable(MotorAxis::RECOMBINE_Z, true);
                    motor_move(MotorAxis::RECOMBINE_Z, 200, false);
                    motor_enable(MotorAxis::RECOMBINE_Z, false);
                    Serial.println("OK jog recz-");
                } else if (strcmp(cmd_buf, "sensors") == 0) {
                    uint8_t raw = sensors_raw_state();
                    Serial.printf("Sensors raw: 0x%02X\n", raw);
                    for (uint8_t i = 0; i < NUM_SENSORS; i++) {
                        Serial.printf("  %s: %s  events=%d\n",
                                      sensor_name(i),
                                      (raw & (1 << i)) ? "BLOCKED" : "clear",
                                      sensor_event_count(i));
                    }
                } else if (strcmp(cmd_buf, "status") == 0) {
                    for (uint8_t i = 0; i < 4; i++) {
                        uint32_t drv_status = motor_get_status(
                            static_cast<MotorAxis>(i));
                        Serial.printf("Motor %d DRV_STATUS: 0x%08X\n",
                                      i, drv_status);
                    }
                } else if (strcmp(cmd_buf, "exit") == 0) {
                    sm_request_stop(ctx);
                } else {
                    Serial.println("Commands: jog feed+/- sel+/- recx+/- recz+/-, sensors, status, exit");
                }
            } else {
                // Outside service mode, limited commands
                if (strcmp(cmd_buf, "state") == 0) {
                    Serial.printf("State: %s  Fault: %s  Pass: %d  "
                                  "FeedExits: %d  BinEntries: %d  Output: %d\n",
                                  sm_state_name(ctx.state),
                                  sm_fault_name(ctx.fault_code),
                                  ctx.current_pass,
                                  ctx.feeder_exits,
                                  ctx.bin_entries,
                                  ctx.output_count);
                } else if (strcmp(cmd_buf, "help") == 0) {
                    Serial.println("Commands: state, help");
                    Serial.println("Enter SERVICE_MODE for motor jog and sensor commands");
                }
            }

            cmd_len = 0;
        } else if (cmd_len < sizeof(cmd_buf) - 1) {
            cmd_buf[cmd_len++] = c;
        }
    }
}

// ============================================================
// Setup
// ============================================================

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) { delay(10); }

    Serial.println();
    Serial.println("========================================");
    Serial.println(" Single-Deck Card Shuffler V1");
    Serial.println(" 2-pass 8-bin random shuffle");
    Serial.println("========================================");

    // Initialize OLED
    display_init();

    // Initialize button pins
    pinMode(PIN_BTN_SHUFFLE, INPUT_PULLUP);
    pinMode(PIN_BTN_STOP, INPUT_PULLUP);

    // Initialize buzzer
    if (PIN_BUZZER >= 0) {
        pinMode(PIN_BUZZER, OUTPUT);
        digitalWrite(PIN_BUZZER, LOW);
    }

    // Initialize sensors (attaches ISRs)
    sensors_init();

    // Initialize state machine (checks NVS, runs self-test)
    sm_init(ctx);

    Serial.println("Setup complete. Running self-test...");
}

// ============================================================
// Main loop
// ============================================================

void loop() {
    // Run non-blocking motor step generation
    motors_run();

    // Handle physical buttons
    handle_buttons();

    // Handle serial commands
    handle_serial_commands();

    // Run state machine
    sm_update(ctx);

    // Update OLED display
    display_update();
}
