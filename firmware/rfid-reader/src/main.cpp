// ShuffleDeck RFID Card Reader — Prototype Firmware
// Reads 13.56MHz RFID-tagged poker cards via RC522, serves identity over WebSocket.

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>

#include "config.h"
#include "card_database.h"
#include "websocket_server.h"

// ── Globals ──

MFRC522 rfid(RC522_SS, RC522_RST);
CardDatabase cardDB;
CardWebSocket wsServer;

enum Mode { MODE_READ, MODE_REGISTER };
Mode currentMode = MODE_READ;

// Debounce tracking
byte lastUID[4] = {0};
byte lastUIDSize = 0;
unsigned long lastReadTime = 0;

// Registration state: holds the UID of a card waiting to be assigned
bool pendingRegistration = false;
byte pendingUID[4];
byte pendingUIDSize = 0;
unsigned long pendingTimestamp = 0;

// ── WiFi Setup ──

void setupWiFi() {
    String ssid = WIFI_SSID;
    if (ssid.length() == 0) {
        Serial.println("[WiFi] No SSID configured, starting AP mode");
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.printf("[WiFi] AP started: %s (password: %s)\n", AP_SSID, AP_PASSWORD);
        Serial.printf("[WiFi] IP: %s\n", WiFi.softAPIP().toString().c_str());
        return;
    }

    Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - start) < WIFI_TIMEOUT_MS) {
        delay(250);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[WiFi] Connection failed, falling back to AP mode");
        WiFi.softAP(AP_SSID, AP_PASSWORD);
        Serial.printf("[WiFi] AP started: %s\n", AP_SSID);
        Serial.printf("[WiFi] IP: %s\n", WiFi.softAPIP().toString().c_str());
    }
}

// ── Serial Command Processing ──

void printHelp() {
    Serial.println();
    Serial.println("=== ShuffleDeck RFID Reader ===");
    Serial.println("Commands:");
    Serial.println("  mode read       - Switch to read mode (continuous scanning)");
    Serial.println("  mode reg        - Switch to registration mode");
    Serial.println("  reg <card>      - Register pending card (e.g. 'reg As' for Ace of spades)");
    Serial.println("  clear           - Wipe all registered cards");
    Serial.println("  count           - Show number of registered cards");
    Serial.println("  help            - Show this help");
    Serial.println();
    Serial.println("Card format: <rank><suit> where rank=2-9,T,J,Q,K,A and suit=s,h,d,c");
    Serial.println("Examples: As=Ace of spades, Td=Ten of diamonds, 2c=Two of clubs");
    Serial.println();
}

void processSerialCommand(String cmd) {
    cmd.trim();
    if (cmd.length() == 0) return;

    if (cmd == "help") {
        printHelp();
    }
    else if (cmd == "mode read") {
        currentMode = MODE_READ;
        pendingRegistration = false;
        Serial.println("[Mode] Switched to READ mode");
    }
    else if (cmd == "mode reg") {
        currentMode = MODE_REGISTER;
        Serial.println("[Mode] Switched to REGISTRATION mode");
        Serial.println("[Mode] Scan a card, then type 'reg <card>' (e.g. 'reg As')");
    }
    else if (cmd.startsWith("reg ")) {
        String cardName = cmd.substring(4);
        cardName.trim();

        if (!pendingRegistration) {
            Serial.println("[Reg] No card scanned yet. Scan a card first.");
            return;
        }
        if (!CardDatabase::isValidCard(cardName.c_str())) {
            Serial.printf("[Reg] Invalid card name: '%s'. Use format like As, Td, 2c\n", cardName.c_str());
            return;
        }

        if (cardDB.registerCard(pendingUID, pendingUIDSize, cardName.c_str())) {
            Serial.printf("[Reg] Success! %d/52 cards registered\n", cardDB.count());
        } else {
            Serial.println("[Reg] Registration failed");
        }
        pendingRegistration = false;
    }
    else if (cmd == "clear") {
        cardDB.clearAll();
        Serial.println("[CardDB] All cards cleared");
    }
    else if (cmd == "count") {
        Serial.printf("[CardDB] %d cards registered\n", cardDB.count());
    }
    else {
        Serial.printf("[Cmd] Unknown command: '%s'. Type 'help' for usage.\n", cmd.c_str());
    }
}

// ── Card Reading ──

bool isSameUID(byte* a, byte aSize, byte* b, byte bSize) {
    if (aSize != bSize) return false;
    for (byte i = 0; i < aSize; i++) {
        if (a[i] != b[i]) return false;
    }
    return true;
}

void handleCardDetected(byte* uid, byte uidSize) {
    String hexUID = uidToHexKey(uid, uidSize);
    unsigned long now = millis();

    if (currentMode == MODE_REGISTER) {
        // Store UID for pending registration
        memcpy(pendingUID, uid, min((byte)4, uidSize));
        pendingUIDSize = uidSize;
        pendingRegistration = true;
        pendingTimestamp = now;

        // Check if already registered
        CardIdentity existing;
        if (cardDB.lookup(uid, uidSize, existing)) {
            Serial.printf("[Reg] Card scanned: UID=%s (currently: %s - %s)\n",
                hexUID.c_str(), existing.short_name, cardLongName(existing.short_name).c_str());
            Serial.println("[Reg] Type 'reg <card>' to reassign, or scan another card");
        } else {
            Serial.printf("[Reg] New card scanned: UID=%s\n", hexUID.c_str());
            Serial.println("[Reg] Type 'reg <card>' to assign (e.g. 'reg As')");
        }
        return;
    }

    // READ mode — debounce check
    if (isSameUID(uid, uidSize, lastUID, lastUIDSize) && (now - lastReadTime) < DEBOUNCE_MS) {
        return; // Same card, within debounce window
    }

    // Update debounce state
    memcpy(lastUID, uid, min((byte)4, uidSize));
    lastUIDSize = uidSize;
    lastReadTime = now;

    // Look up the card
    CardIdentity card;
    if (cardDB.lookup(uid, uidSize, card)) {
        // Build JSON event
        String json = "{\"event\":\"card_read\","
                      "\"card\":\"" + String(card.short_name) + "\","
                      "\"name\":\"" + cardLongName(card.short_name) + "\","
                      "\"uid\":\"" + hexUID + "\","
                      "\"seat\":" + String(SEAT_NUMBER) + ","
                      "\"timestamp\":" + String(now) + "}";

        Serial.println(json);
        wsServer.broadcast(json);
    } else {
        // Unknown card
        String json = "{\"event\":\"unknown_card\","
                      "\"uid\":\"" + hexUID + "\","
                      "\"seat\":" + String(SEAT_NUMBER) + ","
                      "\"timestamp\":" + String(now) + "}";

        Serial.println(json);
        wsServer.broadcast(json);
    }
}

// ── Setup & Loop ──

void setup() {
    Serial.begin(115200);
    delay(500);

    Serial.println();
    Serial.println("========================================");
    Serial.println("  ShuffleDeck RFID Reader v0.1");
    Serial.println("  Prototype - Single Antenna");
    Serial.println("========================================");

    // Init SPI and RC522
    SPI.begin(RC522_SCK, RC522_MISO, RC522_MOSI, RC522_SS);
    rfid.PCD_Init();
    delay(100);

    // Verify reader is connected
    byte version = rfid.PCD_ReadRegister(rfid.VersionReg);
    if (version == 0x00 || version == 0xFF) {
        Serial.println("[RFID] ERROR: RC522 not detected! Check wiring.");
        Serial.println("[RFID] Expected on pins: MOSI=23, MISO=19, SCK=18, SS=5, RST=22");
    } else {
        Serial.printf("[RFID] RC522 firmware version: 0x%02X\n", version);
        rfid.PCD_SetAntennaGain(rfid.RxGain_max); // Max range for reading through felt
        Serial.println("[RFID] Antenna gain set to maximum");
    }

    // Init card database
    cardDB.begin();

    // Init WiFi
    setupWiFi();

    // Init WebSocket server
    wsServer.begin();

    // Ready
    Serial.printf("[Ready] Mode: READ | Seat: %d | WS port: %d\n", SEAT_NUMBER, WS_PORT);
    Serial.printf("[Ready] Cards registered: %d/52\n", cardDB.count());
    Serial.println("[Ready] Type 'help' for commands");
    Serial.println();
}

void loop() {
    // Service WebSocket
    wsServer.loop();

    // Process serial commands
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        processSerialCommand(cmd);
    }

    // Expire pending registration
    if (pendingRegistration && (millis() - pendingTimestamp) > REGISTRATION_TIMEOUT_MS) {
        pendingRegistration = false;
        Serial.println("[Reg] Registration timed out. Scan the card again.");
    }

    // Scan for RFID cards
    if (!rfid.PICC_IsNewCardPresent()) return;
    if (!rfid.PICC_ReadCardSerial()) return;

    handleCardDetected(rfid.uid.uidByte, rfid.uid.size);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    delay(SCAN_INTERVAL_MS);
}
