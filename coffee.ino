
#include "connectivity.h"

// arduino setup
void setup() {
  wifiConnect();
  // mqtt client
  mqttClient.setServer(mqtt_server, 1883);

  Serial.begin(115200, SERIAL_8N1, 2, 15);
  mqttLogger.println("ESP32 hardware serial test on Serial2");

  mqttLogger.println("Starting setup..");
}
char incomingMachineByte = 0;  // for incoming serial data

String machineCommand;
String lastCommand;

void loop() {
  // here the mqtt connection is established
  if (!mqttClient.connected()) {
    connectMqtt();
  }
  wifiConnect();
  if (Serial.available() > 0) {
    while (!machineCommand.endsWith("54")) {
      // read the incoming byte:
      incomingMachineByte = Serial.read();
      // Convert the incoming byte to a hexadecimal string
      char hexString[3];
      sprintf(hexString, "%02X", (unsigned char)incomingMachineByte);
      machineCommand += String(hexString);

      // Check if the last few bytes are "54"
      if (machineCommand.endsWith("54")) {
        if (machineCommand != lastCommand) {
          mqttLogger.println(machineCommand);
          lastCommand = machineCommand;
          machineCommand = "";
        }
      }
    }
  }
}
