#pragma once

// ============================================================
// Pin assignments — ESP32 DevKit
// ============================================================

// IR break-beam sensors at feeder exit, ~20 mm apart.
// Active-low: LOW = beam broken (card present).
// Use pins with interrupt capability (all GPIO on ESP32).
#define PIN_SENSOR1       4    // upstream sensor (card hits this first)
#define PIN_SENSOR2       5    // downstream sensor, ~20 mm after sensor1

// Start/stop button. Active-low with internal pull-up.
#define PIN_BUTTON       15

// Optional: motor enable output. Drive HIGH to run the feeder motor.
// Set to -1 if motor is controlled externally (manual bench rig).
#define PIN_MOTOR        -1

// ============================================================
// Physical geometry — all lengths in mm
// ============================================================

// Distance between sensor1 and sensor2 optical axes.
#define SENSOR_SPACING_MM         20.0

// Standard poker card length (short dimension, direction of feed).
#define CARD_LENGTH_MM            89.0

// ============================================================
// Feed speed — mm/s
// Nominal 80 mm/s for Phase 1. Change per DOE run in Phase 2.
// ============================================================
#define FEED_SPEED_MMS            80.0

// ============================================================
// Derived timing constants (microseconds and milliseconds)
// ============================================================

// Expected transit time from sensor1 leading edge to sensor2 leading edge.
// transit = sensor_spacing / feed_speed
// At 80 mm/s, 20 mm spacing: 250 ms.
#define EXPECTED_TRANSIT_MS       ((unsigned long)((SENSOR_SPACING_MM / FEED_SPEED_MMS) * 1000.0))

// Skew tolerance: flag if transit time differs from expected by more than
// this fraction. 0.30 = 30%.
#define SKEW_TOLERANCE            0.30

// Time for one full card to pass a sensor: card_length / feed_speed.
// At 80 mm/s, 89 mm card: ~1112 ms.
#define CARD_PASS_TIME_MS         ((unsigned long)((CARD_LENGTH_MM / FEED_SPEED_MMS) * 1000.0))

// Minimum gap between consecutive cards at a sensor.
// If the gap is shorter than this, it's suspicious (potential double).
// Set to 30% of card pass time as starting point.
#define MIN_GAP_MS                ((unsigned long)(CARD_PASS_TIME_MS * 0.30))

// Double-feed detection: if both sensors are blocked simultaneously
// for longer than this, declare a double. Normally a single card
// can only block both sensors for (card_length - sensor_spacing) / speed.
// A double-thick stack blocks longer. Threshold = 1.5x single overlap.
#define SINGLE_OVERLAP_MS         ((unsigned long)(((CARD_LENGTH_MM - SENSOR_SPACING_MM) / FEED_SPEED_MMS) * 1000.0))
#define DOUBLE_THRESHOLD_MS       ((unsigned long)(SINGLE_OVERLAP_MS * 1.5))

// Miss detection: motor ran for 2x card length with no sensor trigger.
#define MISS_TIMEOUT_MS           ((unsigned long)((2.0 * CARD_LENGTH_MM / FEED_SPEED_MMS) * 1000.0))

// Jam detection: sensor stays blocked beyond this timeout.
// Set to 3x the time a single card should take to clear.
#define JAM_TIMEOUT_MS            ((unsigned long)(CARD_PASS_TIME_MS * 3.0))

// ============================================================
// Debounce
// ============================================================

// Minimum time between accepted interrupts on a single sensor (us).
// IR break-beam sensors are clean, but cards can chatter at edges.
#define DEBOUNCE_US               2000   // 2 ms
