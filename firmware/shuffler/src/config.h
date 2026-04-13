#pragma once

// ============================================================
// Single-Deck Shuffler — Pin Definitions & Constants
// ESP32 DevKit V1
// ============================================================

// ------------------------------------------------------------
// Stepper motor pins — 4 axes, each with STEP + DIR + ENABLE
// TMC2209 UART shares a single hardware serial bus (Serial2)
// Each driver has a unique UART address (0-3)
// ------------------------------------------------------------

// Feeder motor (singulation roller drive)
#define PIN_FEED_STEP         26
#define PIN_FEED_DIR          27
#define PIN_FEED_EN           25
#define FEED_TMC_ADDR         0

// Selector X-axis (positions over 8 bins)
#define PIN_SEL_STEP          33
#define PIN_SEL_DIR           32
#define PIN_SEL_EN            14
#define SEL_TMC_ADDR          1

// Recombine X-axis (traverses bins for pickup)
#define PIN_REC_X_STEP        19
#define PIN_REC_X_DIR         18
#define PIN_REC_X_EN          17
#define REC_X_TMC_ADDR        2

// Recombine Z-axis elevator (lifts/lowers pickup head)
#define PIN_REC_Z_STEP        16
#define PIN_REC_Z_DIR         4
#define PIN_REC_Z_EN          2
#define REC_Z_TMC_ADDR        3

// TMC2209 shared UART bus (Serial2)
#define PIN_TMC_RX            13
#define PIN_TMC_TX            12
#define TMC_UART_BAUD         115200
#define TMC_R_SENSE           0.11f   // current sense resistor (ohms)

// ------------------------------------------------------------
// Sensor pins — IR break-beam, active-low (LOW = beam broken)
// All pins must support GPIO interrupts
// ------------------------------------------------------------

#define PIN_SENS_FEED_EXIT    34    // feeder exit (card leaves roller)
#define PIN_SENS_POST_SING    35    // post-singulation confirmation
#define PIN_SENS_SEL_THROAT   36    // selector throat transit
#define PIN_SENS_BIN_ENTRY    39    // bin entry confirmation (shared beam)
#define PIN_SENS_REC_PICKUP   23    // recombine pickup confirmation
#define PIN_SENS_OUTPUT       22    // output tray count checkpoint

// Sensor count for iteration
#define NUM_SENSORS           6

// Sensor index constants (for arrays)
#define SENS_IDX_FEED_EXIT    0
#define SENS_IDX_POST_SING    1
#define SENS_IDX_SEL_THROAT   2
#define SENS_IDX_BIN_ENTRY    3
#define SENS_IDX_REC_PICKUP   4
#define SENS_IDX_OUTPUT       5

// ------------------------------------------------------------
// UI pins
// ------------------------------------------------------------

#define PIN_BTN_SHUFFLE       15    // shuffle button, active-low, internal pull-up
#define PIN_BTN_STOP          0     // stop / clear-jam button (BOOT button)
#define PIN_BUZZER            -1    // piezo buzzer disabled (no free GPIO)
// To add buzzer: free a pin by removing one motor axis enable or use I2C GPIO expander

// OLED I2C (SSD1306 128x64)
#define PIN_OLED_SDA          21
#define PIN_OLED_SCL          5     // I2C clock for OLED

#define OLED_ADDR             0x3C
#define OLED_WIDTH            128
#define OLED_HEIGHT           64

// ------------------------------------------------------------
// Mechanical constants
// ------------------------------------------------------------

#define NUM_BINS              8       // storage bins for randomization
#define DECK_SIZE             52      // standard poker deck
#define NUM_PASSES            2       // two-pass shuffle

// Feeder geometry
#define FEED_SPEED_MMS        120.0   // target feed speed (mm/s)
#define CARD_LENGTH_MM        63.0    // poker card short dimension (feed direction)
#define CARD_WIDTH_MM         89.0    // poker card long dimension
#define SENSOR_SPACING_MM     20.0    // feed_exit to post_singulation distance

// Stepper mechanical parameters
#define FEED_STEPS_PER_MM     40.0    // feeder: steps per mm of card travel
#define SEL_STEPS_PER_BIN     200     // selector: steps between adjacent bins
#define REC_X_STEPS_PER_BIN   200     // recombine X: steps between adjacent bins
#define REC_Z_STEPS_DOWN      800     // recombine Z: steps from top to pickup
#define REC_Z_STEPS_UP        800     // recombine Z: steps from pickup to clear

// Motor speeds (steps/sec)
#define FEED_SPEED_SPS        ((uint32_t)(FEED_SPEED_MMS * FEED_STEPS_PER_MM))
#define SEL_SPEED_SPS         4000
#define REC_X_SPEED_SPS       4000
#define REC_Z_SPEED_SPS       2000

// Motor current (mA RMS)
#define FEED_CURRENT_MA       600
#define SEL_CURRENT_MA        800
#define REC_X_CURRENT_MA      800
#define REC_Z_CURRENT_MA      600

// ------------------------------------------------------------
// Timing constants
// ------------------------------------------------------------

// Expected transit: feed_exit to post_singulation
#define EXPECTED_TRANSIT_MS   ((unsigned long)((SENSOR_SPACING_MM / FEED_SPEED_MMS) * 1000.0))

// Card pass time at a single sensor
#define CARD_PASS_TIME_MS     ((unsigned long)((CARD_LENGTH_MM / FEED_SPEED_MMS) * 1000.0))

// Jam timeout: sensor blocked for too long
#define JAM_TIMEOUT_MS        ((unsigned long)(CARD_PASS_TIME_MS * 3))

// Miss timeout: no sensor trigger after starting feed
#define MISS_TIMEOUT_MS       ((unsigned long)((2.0 * CARD_LENGTH_MM / FEED_SPEED_MMS) * 1000.0))

// Inter-card gap: minimum time between consecutive cards
#define MIN_GAP_MS            ((unsigned long)(CARD_PASS_TIME_MS * 0.4))

// Selector settle time after move (ms)
#define SEL_SETTLE_MS         20

// Recombine pickup dwell time (ms)
#define REC_PICKUP_DWELL_MS   50

// Debounce for IR sensors (microseconds)
#define DEBOUNCE_US           2000

// Button debounce (ms)
#define BTN_DEBOUNCE_MS       200

// Self-test jog distance (steps)
#define SELFTEST_JOG_STEPS    50

// Maximum jam retries per segment before hard fault
#define MAX_JAM_RETRIES       3

// Reverse jog on jam (steps)
#define JAM_REVERSE_STEPS     100

// NVS namespace
#define NVS_NAMESPACE         "shuffler"
#define NVS_KEY_STATE         "fault_st"
#define NVS_KEY_PASS          "fault_pass"
#define NVS_KEY_CARD_COUNT    "fault_cnt"
