#pragma once

#include <cstdint>

// ============================================================
// Shuffler State Machine
// ============================================================

enum class ShufflerState : uint8_t {
    BOOT_SELFTEST,      // power-on self-test: sensors clear, jog each motor
    IDLE,               // waiting for shuffle button press
    FEEDING_PASS_1,     // singulating cards, routing to random bins (pass 1)
    RECOMBINE_1,        // picking up bin stacks into temp stack
    FEEDING_PASS_2,     // singulating temp stack through bins again (pass 2)
    RECOMBINE_2,        // picking up final bin stacks to output tray
    COMPLETE,           // deck delivered, return to idle after delay
    FAULT_FEEDER,       // jam or error in feeder subsystem
    FAULT_SELECTOR,     // selector positioning or routing error
    FAULT_RECOMBINE,    // recombine pickup or handoff error
    FAULT_COUNT,        // card count invariant violated
    FAULT_POWER,        // brownout recovery — interrupted state in NVS
    SERVICE_MODE,       // manual jog, sensor readout
};

// Fault sub-type for diagnostics
enum class FaultCode : uint8_t {
    NONE = 0,
    FEED_JAM,           // card stuck in feeder
    FEED_MISS,          // feeder ran but no card detected
    FEED_DOUBLE,        // double-feed detected
    SEL_TIMEOUT,        // selector did not reach position
    SEL_MISROUTE,       // card not detected at expected bin
    BIN_JAM,            // card stuck at bin entry
    REC_PICKUP_FAIL,    // recombine failed to pick up stack
    REC_ELEVATOR_JAM,   // Z-axis jam
    COUNT_MISMATCH,     // per-pass count invariant violated
    COUNT_FINAL,        // final deck != 52
    SENSOR_FAIL,        // sensor stuck or unresponsive during self-test
    POWER_INTERRUPTED,  // NVS indicates interrupted shuffle
    MOTOR_COMM_FAIL,    // TMC2209 UART communication failure
};

// Card event types from sensors
enum class CardEvent : uint8_t {
    NONE = 0,
    FEED_EXIT,          // card exited feeder roller
    POST_SINGULATE,     // card confirmed singulated
    SEL_TRANSIT,        // card transited selector throat
    BIN_ENTRY,          // card entered bin
    REC_PICKUP,         // stack picked up from bin
    OUTPUT_COUNT,       // card counted at output
};

// State machine context — holds all running state
struct ShufflerContext {
    ShufflerState state;
    ShufflerState prev_state;       // for fault recovery
    FaultCode fault_code;
    uint8_t current_pass;           // 1 or 2

    // Card counts — per-pass invariant tracking
    uint16_t feeder_exits;          // cards that exited feeder
    uint16_t post_singulations;     // cards confirmed singulated
    uint16_t selector_entries;      // cards that entered selector
    uint16_t bin_entries;           // cards confirmed in bins
    uint16_t bin_counts[8];         // per-bin card count
    uint16_t recombine_out;         // cards recombined
    uint16_t output_count;          // cards at output checkpoint

    // Current card routing
    uint8_t target_bin;             // bin assignment for current card
    uint8_t current_sel_pos;        // current selector position (0-7)
    uint8_t current_rec_pos;        // current recombine X position

    // Recombine state
    uint8_t recombine_bin_idx;      // which bin we're picking up from

    // Jam recovery
    uint8_t jam_retries;            // retries on current segment

    // Timing
    unsigned long state_enter_ms;   // millis() when current state entered
    unsigned long last_card_ms;     // millis() of last card event
    unsigned long feed_start_ms;    // millis() when current feed started

    // Flags
    bool shuffle_requested;         // button pressed
    bool stop_requested;            // stop button pressed
    bool service_requested;         // service mode entry requested
    bool selftest_passed;           // boot self-test result
};

// Initialize context to power-on defaults
void sm_init(ShufflerContext& ctx);

// Run one iteration of the state machine (call from loop())
void sm_update(ShufflerContext& ctx);

// Signal a card event to the state machine
void sm_card_event(ShufflerContext& ctx, CardEvent event);

// Request state transitions from UI
void sm_request_shuffle(ShufflerContext& ctx);
void sm_request_stop(ShufflerContext& ctx);
void sm_request_service(ShufflerContext& ctx);
void sm_request_clear_fault(ShufflerContext& ctx);

// Get human-readable state name
const char* sm_state_name(ShufflerState state);
const char* sm_fault_name(FaultCode code);
