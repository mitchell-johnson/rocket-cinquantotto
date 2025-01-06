
#include "connectivity.h"
HardwareSerial SerialGP(1); // Use UART1 for communication with the coffee machine

// arduino setup
void setup() {
  wifiConnect();
  // mqtt client
  mqttClient.setServer(mqtt_server, 1883);

  // Serial.begin(115200, SERIAL_8N1, 2, 15);

  Serial.begin(115200);                      // For debugging via Serial Monitor
  SerialGP.begin(115200, SERIAL_8N1, 2, 15);  // Adjust baud rate and pins as needed

  mqttLogger.println("ESP32 hardware serial test on Serial");

  mqttLogger.println("Starting setup..");
}
char incomingMachineByte = 0;  // for incoming serial data


// Buffer to store incoming data
uint8_t buffer[256];
uint16_t bufferIndex = 0;

  String packetString;
  String lastPacketString;

void processPacket(uint8_t *packetBuffer, uint16_t packetLength) {
  uint8_t byteCount = packetBuffer[2];
  uint8_t command = packetBuffer[3];
  packetString = "";
  // Convert packet to a hexadecimal string for logging

  for (uint16_t i = 0; i < packetLength; i++) {
    char hexString[3];
    sprintf(hexString, "%02X", packetBuffer[i]);
    packetString += String(hexString);
  }

  // Send packet over MQTT
  if(packetString != lastPacketString){
    mqttLogger.println(packetString);
    lastPacketString = packetString;
  }

  // Additional parsing can be added here if needed
}

void loop() {
  // here the mqtt connection is established
  while (SerialGP.available()) {
    if (!mqttClient.connected()) {
      connectMqtt();
    }
    wifiConnect();
    uint8_t incomingByte = SerialGP.read();
    buffer[bufferIndex++] = incomingByte;

    // Check if we have at least 3 bytes to start processing (Frame Header + Byte Count)
    if (bufferIndex >= 4) {
      // Look for Frame Header at the start of the buffer
      if (buffer[0] == 0x5A && buffer[1] == 0xA5) {
        uint8_t byteCount = buffer[2];

        // Calculate total packet length (Byte Count + Command + CRC if present)
        uint16_t packetLength = 3 + byteCount;  // 3 bytes before Byte Count

        // Check if the entire packet has been received
        if (bufferIndex >= packetLength) {
          // Process the packet
          processPacket(buffer, packetLength);

          // Reset the buffer for the next packet
          bufferIndex = 0;
        }
      } else {
        // Shift buffer to remove the first byte and try to find the Frame Header again
        for (uint16_t i = 1; i < bufferIndex; i++) {
          buffer[i - 1] = buffer[i];
        }
        bufferIndex--;
      }
    }
  }
}
