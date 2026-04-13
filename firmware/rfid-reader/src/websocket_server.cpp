#include "websocket_server.h"

CardWebSocket* CardWebSocket::_instance = nullptr;

void CardWebSocket::begin() {
    _instance = this;
    _ws.begin();
    _ws.onEvent(CardWebSocket::onEvent);
    Serial.printf("[WS] WebSocket server started on port %d\n", WS_PORT);
}

void CardWebSocket::loop() {
    _ws.loop();
}

void CardWebSocket::broadcast(const String& json) {
    _ws.broadcastTXT(json);
    if (_clients > 0) {
        Serial.printf("[WS] Broadcast to %d client(s)\n", _clients);
    }
}

void CardWebSocket::onEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
    if (!_instance) return;

    switch (type) {
        case WStype_DISCONNECTED:
            _instance->_clients = max(0, _instance->_clients - 1);
            Serial.printf("[WS] Client #%u disconnected (%d remaining)\n", num, _instance->_clients);
            break;

        case WStype_CONNECTED:
            _instance->_clients++;
            Serial.printf("[WS] Client #%u connected (%d total)\n", num, _instance->_clients);
            // Send a hello so clients know they're connected
            _instance->_ws.sendTXT(num, "{\"event\":\"connected\",\"device\":\"shuffledeck-rfid\"}");
            break;

        case WStype_TEXT:
            // Could handle incoming commands here in future
            Serial.printf("[WS] Received from #%u: %s\n", num, payload);
            break;

        default:
            break;
    }
}
