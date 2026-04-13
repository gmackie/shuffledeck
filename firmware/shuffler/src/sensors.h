#pragma once

#include <cstdint>
#include "state_machine.h"

// ============================================================
// Sensor Reading, ISRs, Event Classification
// ============================================================

// Initialize sensor GPIO pins and attach ISRs
void sensors_init();

// Check if all sensors read clear (not blocked)
// Used during boot self-test
bool sensors_all_clear();

// Check if a specific sensor is currently blocked
bool sensor_is_blocked(uint8_t sensor_idx);

// Poll for pending card events (call from main loop)
// Returns the next unprocessed event, or CardEvent::NONE
CardEvent sensors_poll_event();

// Get the timestamp (micros) of the last event
unsigned long sensors_last_event_us();

// Reset all sensor event state (between passes, after fault clear)
void sensors_reset();

// Get raw sensor state for service mode display
// Returns bitmask: bit N = sensor N blocked
uint8_t sensors_raw_state();

// Get sensor name string by index
const char* sensor_name(uint8_t idx);

// Sensor diagnostic: count of events per sensor since last reset
uint16_t sensor_event_count(uint8_t idx);

// Check for stuck sensors (blocked for too long without state change)
// Returns sensor index of stuck sensor, or -1 if none
int8_t sensors_check_stuck(unsigned long timeout_ms);
