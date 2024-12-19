
#include "wifi_secrets.h"
#include <WiFi.h>
#include <PubSubClient.h>
// #include "MqttLogger.h"
#include <MqttLogger.h>

#define CLIENT_ID "coffee_machine"
#define DEVICE_NAME "Coffee Machine"
const char *ssid = WIFI_SSID;
const char *password = WIFI_PASSWORD;
const char *mqtt_server = MQTT_SERVER;


WiFiClient espClient;
PubSubClient mqttClient(espClient);
MqttLogger mqttLogger(mqttClient, "mqttlogger/log", MqttLoggerMode::MqttAndSerial);

// connect to wifi network
void wifiConnect() {
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println(WiFi.status());
    Serial.println("Connecting to " + String(ssid));
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    delay(1000);
    Serial.print(".");
    if ((WiFi.status() == WL_CONNECTED)) {
      Serial.println("\nWiFi connected. IP: " + WiFi.localIP().toString());
      break;
    }
  }
}

void connectMqtt() {
  mqttLogger.println("\nConnecting to MQTT...");
  while (!mqttClient.connected()) {
    // mqttClient.setWill("home/" CLIENT_ID "/status", "offline", true, 1);
    if (mqttClient.connect(CLIENT_ID, "home/" CLIENT_ID "/status", 1, true, "offline")) {
      mqttLogger.println("connected");
      mqttClient.publish("home/" CLIENT_ID "/status", "online", true);
    } else {
      Serial.print(".");
      delay(1000);
    }
  }
  mqttLogger.println("\nMQTT connected!");
  mqttClient.subscribe("/hello");
}
