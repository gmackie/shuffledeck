#pragma once

#include <cstdint>

// ============================================================
// Motor Control — TMC2209 UART + Step/Dir
// ============================================================

// Motor axis identifiers
enum class MotorAxis : uint8_t {
    FEEDER = 0,
    SELECTOR_X,
    RECOMBINE_X,
    RECOMBINE_Z,
    NUM_AXES
};

// Initialize all TMC2209 drivers and GPIO pins
// Returns true if all drivers respond on UART
bool motors_init();

// Enable/disable individual motor
void motor_enable(MotorAxis axis, bool enabled);

// Enable/disable all motors
void motors_enable_all(bool enabled);

// Move a motor by a given number of steps at the configured speed
// Blocking call — returns when move is complete
// dir: true = forward/CW, false = reverse/CCW
void motor_move(MotorAxis axis, int32_t steps, bool dir);

// Move a motor at a given speed (steps/sec), non-blocking start
// Call motor_is_moving() to check completion
void motor_start(MotorAxis axis, uint32_t speed_sps, bool dir);

// Stop a motor (decelerate)
void motor_stop(MotorAxis axis);

// Stop all motors immediately
void motors_stop_all();

// Check if a motor is currently moving
bool motor_is_moving(MotorAxis axis);

// Run step pulses — call frequently from loop() for non-blocking moves
void motors_run();

// Move selector to a specific bin position (0-7)
// Calculates delta from current position and moves
void selector_move_to_bin(uint8_t bin, uint8_t& current_pos);

// Move recombine X to a specific bin position (0-7)
void recombine_x_move_to_bin(uint8_t bin, uint8_t& current_pos);

// Recombine Z-axis: lower pickup head
void recombine_z_lower();

// Recombine Z-axis: raise pickup head
void recombine_z_raise();

// Self-test jog: move each axis a small amount and back
// Returns true if all axes respond (no stall detected)
bool motors_selftest_jog();

// Reverse jog for jam recovery
void motor_reverse_jog(MotorAxis axis, int32_t steps);

// Check TMC2209 communication for a specific driver
bool motor_check_comm(MotorAxis axis);

// Get driver status flags (overtemp, short, etc.)
uint32_t motor_get_status(MotorAxis axis);
