#pragma once

#include <Arduino.h>
#include <Preferences.h>

// ── Card Identity ──

struct CardIdentity {
    char suit;          // 's', 'h', 'd', 'c'
    char rank;          // '2'-'9', 'T', 'J', 'Q', 'K', 'A'
    char short_name[4]; // e.g. "As", "Td", "2c" — null terminated
};

// All 52 valid short names for validation
static const char* ALL_CARDS[] = {
    "2s","3s","4s","5s","6s","7s","8s","9s","Ts","Js","Qs","Ks","As",
    "2h","3h","4h","5h","6h","7h","8h","9h","Th","Jh","Qh","Kh","Ah",
    "2d","3d","4d","5d","6d","7d","8d","9d","Td","Jd","Qd","Kd","Ad",
    "2c","3c","4c","5c","6c","7c","8c","9c","Tc","Jc","Qc","Kc","Ac",
};
static const int NUM_CARDS = 52;

// Convert UID bytes to a hex key string for NVS storage (e.g. "A1B2C3D4")
inline String uidToHexKey(byte* uid, byte size) {
    String key = "";
    for (byte i = 0; i < size && i < 4; i++) {
        if (uid[i] < 0x10) key += "0";
        key += String(uid[i], HEX);
    }
    key.toUpperCase();
    return key;
}

// Human-readable card name
inline String cardLongName(const char* short_name) {
    if (!short_name || strlen(short_name) < 2) return "Unknown";

    String name = "";
    switch (short_name[0]) {
        case '2': name = "Two"; break;
        case '3': name = "Three"; break;
        case '4': name = "Four"; break;
        case '5': name = "Five"; break;
        case '6': name = "Six"; break;
        case '7': name = "Seven"; break;
        case '8': name = "Eight"; break;
        case '9': name = "Nine"; break;
        case 'T': name = "Ten"; break;
        case 'J': name = "Jack"; break;
        case 'Q': name = "Queen"; break;
        case 'K': name = "King"; break;
        case 'A': name = "Ace"; break;
        default:  return "Unknown";
    }
    name += " of ";
    switch (short_name[1]) {
        case 's': name += "Spades"; break;
        case 'h': name += "Hearts"; break;
        case 'd': name += "Diamonds"; break;
        case 'c': name += "Clubs"; break;
        default:  return "Unknown";
    }
    return name;
}

// ── Card Database (NVS-backed) ──

class CardDatabase {
public:
    void begin() {
        _prefs.begin(NVS_NAMESPACE, false);
        _count = _prefs.getInt("count", 0);
        Serial.printf("[CardDB] Loaded, %d cards registered\n", _count);
    }

    // Look up a card by UID. Returns true if found.
    bool lookup(byte* uid, byte uidSize, CardIdentity& out) {
        String key = uidToHexKey(uid, uidSize);
        String val = _prefs.getString(key.c_str(), "");
        if (val.length() < 2) return false;

        out.rank = val.charAt(0);
        out.suit = val.charAt(1);
        strncpy(out.short_name, val.c_str(), 3);
        out.short_name[3] = '\0';
        return true;
    }

    // Register a card. short_name like "As", "Td", etc.
    bool registerCard(byte* uid, byte uidSize, const char* short_name) {
        if (!isValidCard(short_name)) return false;

        String key = uidToHexKey(uid, uidSize);

        // Check if this UID was already registered
        String existing = _prefs.getString(key.c_str(), "");
        if (existing.length() == 0) {
            _count++;
            _prefs.putInt("count", _count);
        }

        _prefs.putString(key.c_str(), short_name);
        Serial.printf("[CardDB] Registered UID %s -> %s (%s)\n",
            key.c_str(), short_name, cardLongName(short_name).c_str());
        return true;
    }

    // Remove a card by UID
    bool removeCard(byte* uid, byte uidSize) {
        String key = uidToHexKey(uid, uidSize);
        if (_prefs.getString(key.c_str(), "").length() > 0) {
            _prefs.remove(key.c_str());
            _count = max(0, _count - 1);
            _prefs.putInt("count", _count);
            return true;
        }
        return false;
    }

    // Wipe all registered cards
    void clearAll() {
        _prefs.clear();
        _count = 0;
        Serial.println("[CardDB] All cards cleared");
    }

    int count() const { return _count; }

    // Validate a short card name
    static bool isValidCard(const char* name) {
        if (!name || strlen(name) < 2) return false;
        for (int i = 0; i < NUM_CARDS; i++) {
            if (strcmp(ALL_CARDS[i], name) == 0) return true;
        }
        return false;
    }

private:
    Preferences _prefs;
    int _count = 0;
};
