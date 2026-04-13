#pragma once

// ── RC522 SPI Pin Definitions (ESP32 DevKit) ──
// Using default VSPI bus
#define RC522_MOSI  23
#define RC522_MISO  19
#define RC522_SCK   18
#define RC522_SS    5    // SDA/CS pin
#define RC522_RST   22

// ── WiFi Configuration ──
// Set these to your network, or leave empty for AP mode fallback
#define WIFI_SSID       ""
#define WIFI_PASSWORD   ""
#define WIFI_TIMEOUT_MS 10000

// ── AP Mode Fallback ──
#define AP_SSID     "ShuffleDeck-RFID"
#define AP_PASSWORD "shuffle123"

// ── WebSocket ──
#define WS_PORT 81

// ── Reader Settings ──
#define SEAT_NUMBER     1           // Which seat this reader is at
#define DEBOUNCE_MS     2000        // Don't re-report same card within this window
#define SCAN_INTERVAL_MS 100        // Poll interval between scans
#define REGISTRATION_TIMEOUT_MS 30000  // Time to complete registration after scan

// ── NVS ──
#define NVS_NAMESPACE "carddb"
