//Chat gpt generate code to parse the messages
/*
  Arduino code to parse DWIN DGUS UART packets and print them.

  This code assumes the packets are coming in through the Serial port.
  It reads the incoming bytes, assembles them into packets based on the headers,
  validates the checksum, and then parses and prints the packet contents.

  The code supports:
  - Variable write commands (Command 0x82)
  - Checksum validation according to the DWIN protocol
*/

#define BUFFER_SIZE 256  // Adjust as needed for larger packets

uint8_t buffer[BUFFER_SIZE];
uint16_t bufferIndex = 0;

void setup() {
  Serial.begin(115200);  // Set baud rate according to your device
  Serial.println("Starting DWIN DGUS Packet Parser...");
}

void loop() {
  // Read bytes from Serial
  while (Serial.available()) {
    uint8_t byte = Serial.read();
    parseByte(byte);
  }
}

void parseByte(uint8_t byte) {
  // Add byte to buffer
  if (bufferIndex < BUFFER_SIZE) {
    buffer[bufferIndex++] = byte;
  } else {
    // Buffer overflow, reset buffer
    bufferIndex = 0;
  }

  // Try to parse packets from the buffer
  while (bufferIndex >= 4) {  // Minimum packet size is 4 bytes
    if (isValidHeader(buffer)) {
      uint16_t length = ((uint16_t)buffer[2] << 8) | buffer[3];
      uint16_t packetSize = length + 4 + 2;  // Header + Length + Data + Checksum

      if (bufferIndex >= packetSize) {
        if (validateChecksum(buffer, packetSize)) {
          parsePacket(buffer, packetSize);
        } else {
          Serial.println("Invalid checksum");
        }
        removeProcessedBytes(packetSize);
      } else {
        // Wait for more data
        break;
      }
    } else {
      // Invalid header, remove first byte and try again
      shiftBuffer();
    }
  }
}

bool isValidHeader(uint8_t* buf) {
  // Valid headers: 0x5A 0xA5, 0x5E 0xA5, 0x5A 0xA7, etc.
  if ((buf[0] == 0x5A && buf[1] == 0xA5) ||
      (buf[0] == 0x5E && buf[1] == 0xA5) ||
      (buf[0] == 0x5A && buf[1] == 0xA7) ||
      (buf[0] == 0x5E && buf[1] == 0xA7)) {
    return true;
  }
  return false;
}

bool validateChecksum(uint8_t* buf, uint16_t packetSize) {
  // Sum all bytes from Length to the last data byte
  uint16_t sum = 0;
  for (uint16_t i = 2; i < packetSize - 2; i++) {
    sum += buf[i];
  }
  // Calculate checksum: checksum = 0xFFFF - sum + 1
  uint16_t calculatedChecksum = 0xFFFF - sum + 1;
  // Extract checksum from packet
  uint16_t packetChecksum = ((uint16_t)buf[packetSize - 2] << 8) | buf[packetSize - 1];
  return calculatedChecksum == packetChecksum;
}

void parsePacket(uint8_t* buf, uint16_t packetSize) {
  uint8_t command = buf[4];
  Serial.print("Command: 0x");
  Serial.println(command, HEX);

  switch (command) {
    case 0x82:  // Write variable
      parseWriteVariable(buf);
      break;
    // Add cases for other commands if needed
    default:
      Serial.println("Unknown command");
      break;
  }
}

void parseWriteVariable(uint8_t* buf) {
  uint16_t address = ((uint16_t)buf[5] << 8) | buf[6];
  uint16_t dataLength = ((uint16_t)buf[7] << 8) | buf[8];  // Number of words
  Serial.print("Address: 0x");
  Serial.print(address, HEX);
  Serial.print(", Data Length: ");
  Serial.println(dataLength);

  Serial.print("Data: ");
  for (uint16_t i = 0; i < dataLength * 2; i += 2) {
    uint16_t data = ((uint16_t)buf[9 + i] << 8) | buf[9 + i + 1];
    Serial.print("0x");
    Serial.print(data, HEX);
    Serial.print(" ");
  }
  Serial.println();
}

void removeProcessedBytes(uint16_t count) {
  // Shift remaining bytes to the beginning of the buffer
  for (uint16_t i = 0; i < bufferIndex - count; i++) {
    buffer[i] = buffer[i + count];
  }
  bufferIndex -= count;
}

void shiftBuffer() {
  // Remove the first byte and shift the buffer
  for (uint16_t i = 0; i < bufferIndex - 1; i++) {
    buffer[i] = buffer[i + 1];
  }
  bufferIndex--;
}

