#pragma once

#include <Arduino.h>
#include <WebSocketsServer.h>
#include "config.h"

class CardWebSocket {
public:
    void begin();
    void loop();
    void broadcast(const String& json);
    int clientCount() const { return _clients; }

private:
    WebSocketsServer _ws = WebSocketsServer(WS_PORT);
    int _clients = 0;

    static void onEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length);
    static CardWebSocket* _instance;
};
