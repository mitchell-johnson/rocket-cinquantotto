# rocket-cinquantotto
Investigation into hacking the rocket cinquantotto USB UART output to export information and control the device. The ultimate goal is to integrate the machine into homeassistant will full control.  

![image](https://github.com/user-attachments/assets/718cc00b-b636-47ad-806b-d4dbc2fd8759)


The screen itself is the DMT48320C035_06WT the USB cable plugs stright into the Rx & Tx pins in the back

![IMG_2462](https://github.com/user-attachments/assets/4b0e62d0-8b92-4025-9ef8-901fb6a586d9)

![IMG_2464](https://github.com/user-attachments/assets/c180d525-ae59-4cd2-8786-0df666e46d8f)
![IMG_2466](https://github.com/user-attachments/assets/0f89e855-ef04-4339-9743-c9e3b79692c4)
![IMG_2467](https://github.com/user-attachments/assets/20af023c-025d-4f8d-9439-e8c7636d03a0)

Writing a quick Arduio sketch on my Lolin D32 Board I am getting the following Hex strings when idle. Not sure what they mean yet. Im assuming they are the temp readings.
Based on the spec sheet using 115200 baud and strings are hex
#### Segment: `5AA509821041000100051654`
- `5AA5098210410001`: Header.
- `00051654`: Payload.

Also this random payload in there
#### Segment: `213014010100051654FF`
- This seems different, possibly indicating a different message type or corrupted data.
- `213014010100051654FF`: New potential header and payload.

Random set of payloads
- 5A A5 09 | 82 10 41 00 01 00 05 16 54 
- 5A A5 09 | 82 10 41 00 01 00 05 16 54 
- 5A A5 09 | A2 10 53 10 A1 A4 A5 16 54  
- 7A A5 09 | 82 12 E1 80 81 00 85 9F 54  
- 5A A5 09 | 82 10 41 00 01 00 05 16 54

5EA509821041000100051654
5A696118140101004111F5
5AA709821041000100058BF5
5AA5098210418001004111FF
5AA7098210410001004111F5
5AA50982105040071654
5EA509C310410001000516EA
5AA509821041000180058B54
5AA709821050409011F5
5AA5098210410001000516EA
5AA509821041000100051654
5AA5098610410001800516EA
5AA509821041000100051654
5A694230140040051654
5AA50982104100404111F5
5AA509821041000100051654
5A794230140140058B54
5AA509861041000100051654
5AA5098210418001004311F5
5AA5098210410040058B54
5AA5098210410040051654
5A7B61301401400516AE
5AA5098210500180051654
5AA509C31041000380051654
5AA509C31041000100051654
5AA50982104100404111F5
5AA709821041000100051654
5AA709C11041000180051654
5AA509821041000100051654
5AA509821041000100051654
5AA509821041800100051654
5AA5098210410040058B54
5AA509821041000100051654
5AA5098210410040351654
5AA50982106801004111FD
5AA5098210410001800516EA
DA69423014010500058B54
5AA509C310410001004111F5
5AA5098210500180051654
5AA70982105040058B54
5AA509821041000100058B54
5AA509861041000100051654
5AA509C110500500053654
5AA50BC11041000100078B54
5AA509C110418001004111F5
5A69423014010100058B54
5A694230140105000516EA
DAA509821041000100051654
5AA5098210500100051654
FFA509C310418001004111F5
5AA509C1105001004111FD
5AA5098210410040B8D011FD
5AA509821041000100051654
5AA50982104100C0051654
5A69611814010D00051654
5AA5098210500100053654
5AA509821041000180051654
5AA5098210504054
5AA5098210500100051654
5AA509821041000100051654
5AA709821041000100051654
5AA509C110418001004111F5
5AA509C11041800100051654
5AA5098210410001000516EA
5AA5098210410001004311F5
5AA5098210410001004311F5
5EA5098210410001000516EA
5AA509821041000100051654
5EA509C11041000100051654
5AA509821041000100051654
5A696130140101004111F5
DA694230140101000516EA
5AA5098210410003800516AA
5AA509821041000100051654
5EA509C110410001804111FD
5AA709821041000100051654
5AA509C11041000180051654
5A796118140040058B54
5AA5098210418001004111F5
5EA509821041000100051654
5AAD098210410040058B54
DA69611814010100C311F5
5A694630140040051654
5A694238140140051654
5AA5098210500180058B54
5AA7098210500100051654
5AA709821041000180051654
5AA509821041000100071654
5E694230140101800516EA
5AA509821041000100051654
5AA5098210418001004111F5
5AA509821041000100051654
5AA509821041000100051654
5AA5098210418001004111F5
5AA509861041000100051654
5AA509821041000100051654
5AA509821041800180051654
5AA509821041000100051654
5EA5098210410001004111FD
5AA509821041000100051654
5AA5098210430001004111F5
5AA5098210410040051654
5AA509821041000100051654
5AA709821041000180051654
5AA509821041000180051654
5AA509861041000100051654
5AA509821041000100058B54
5AA5098210410001004111F5
5AA509861041800100051654
5EA7098210500100051654
5A694218148001004111F5
5AA509821041000100051654
5AA509821041000100051654
5AA5098610438001000516EA
5AA509C110410001000516EA
5AA509821041000180051654
5A5A581041000100051654
5AA5098210430001004111F5
EDA509861041000100051654
5EA509C310410001004111FD
5AA509C11041000100051654
5AA509821041000180051654
5AA5098210410040058B54
5AA509C11041000100051654
5AA5098210500180051654
5AA5098210500100058B54
5AA509C11041000100051654
5AA509821041000100051654
5AA509821041800100058B54
5A69423814010100051654
5AA509821041000100051654
5AA50B8210418001000516EA
5AA5098210418001000516EA
5AA509821041000100051654
5AA5098210410040058B54
5AA709C11041800180051654
5AA509821041000100051654
5AA509821041000100058B54
5AA509821041000100058B54
5AA509821041000100071654
5AA509821041000300051654
5A694230140105004111F5
5AA709C31041000100051654
5AA5098210410040051654



In this series of the machine was heating up with times going . I would be expecting it to be producing temperature updates. I have splint the series by ending in 54 for the most part but then again by 5A as there were lots that didn't end in 54. For those that didn't end up in 54 seem to end in F5 with others EA, FF, FD, AE (maybe), 

5AA | 50 = the the first 5 is not the length. many packets have the same sequence but different lengths. However they are more frequently 22 chars it could also be 5A | A5 | 

- in the sequence there are 99 instances of 5AA50 and 98 of those are 5A|A5|09 with one being 5A|A5|0B


- different combos of the first 4 bytes
1. `5EA5`: 8 times
2. `5A69`: 11 times
3. `5AA7`: 13 times
4. `5AA5`: 99 times
5. `5AAD`: 1 times
6. `DA69`: 3 times
7. `FFA5`: 1 time
8. `5E69`: 1 time




5AA509821041000100051654 seems to be a common status message. Maybe a keep alive. 

Screenshots from the programming guide 
![Uploading image.png…]()
![Uploading image.png…]()

Certainly! Below is the Arduino code that parses the UART packets from your coffee machine's DWIN DGUS screen and prints the decoded information. This code reads incoming bytes from the serial port, assembles them into packets according to the DWIN protocol, validates the checksum, and then interprets the data.

```cpp
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
```

### How the Code Works

- **Buffering Incoming Data**: The code reads incoming bytes from the serial port and stores them in a buffer.
- **Packet Detection**: It checks for valid packet headers (`0x5A 0xA5`, `0x5E 0xA5`, etc.).
- **Packet Assembly**: Once a valid header is detected, it reads the length of the packet and waits until all bytes are received.
- **Checksum Validation**: It calculates the checksum using the DWIN protocol method and compares it with the checksum in the packet.
- **Packet Parsing**: If the checksum is valid, it parses the packet based on the command (e.g., `0x82` for write variable).
- **Data Interpretation**: It extracts the address and data from the packet and prints them out.

### Checksum Calculation Details

- **Sum Calculation**: Adds all bytes from the **Length** field up to the last byte of the **Data** field.
- **Checksum Formula**: `Checksum = 0xFFFF - Sum + 1`
- **Verification**: The calculated checksum is compared with the checksum provided at the end of the packet.

### Example Output

When the parser receives a packet like:

```
5E A5 09 82 10 41 00 01 00 05 16 54
```

The output will be:

```
Command: 0x82
Address: 0x1041, Data Length: 1
Data: 0x5
```

### Using the Code

1. **Connect the Arduino** to the serial output of your coffee machine's UART interface.
2. **Set the Baud Rate**: Ensure that the baud rate (`115200` in the code) matches the UART settings of your device.
3. **Upload the Code**: Upload the code to your Arduino board.
4. **Monitor the Output**: Open the Serial Monitor in the Arduino IDE to see the parsed packets and data.

### Notes

- **Adjust Buffer Size**: If you expect larger packets, increase the `BUFFER_SIZE`.
- **Command Handling**: Currently, only the `0x82` (write variable) command is implemented. You can add cases for other commands as needed.
- **Data Interpretation**: The code prints the raw data values. You might need to apply scaling factors or conversions based on how the data represents sensor readings (e.g., temperature).

### Adding Data Interpretation

If you know that certain addresses correspond to specific sensors (e.g., temperature), you can modify the `parseWriteVariable` function to interpret the data accordingly:

```cpp
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

    // Interpret data based on address
    if (address == 0x1041) {  // Example address for temperature
      float temperature = data / 10.0;  // Assuming data is in tenths of degrees
      Serial.print(temperature);
      Serial.print(" °C ");
    } else {
      Serial.print("0x");
      Serial.print(data, HEX);
      Serial.print(" ");
    }
  }
  Serial.println();
}
```

### Testing the Code with Sample Data

If you want to test the code with the sample data you provided, you can simulate serial input by modifying the `loop` function:

```cpp
void loop() {
  // Sample data string
  const char* sampleData = "5EA5098210410001000516545AA709821041000100058BF5";
  // Convert hex string to bytes and parse
  parseHexString(sampleData);
  // Prevent re-running
  while (1);
}

void parseHexString(const char* hexString) {
  uint8_t len = strlen(hexString);
  char byteString[3] = {0};
  for (uint8_t i = 0; i < len; i += 2) {
    byteString[0] = hexString[i];
    byteString[1] = hexString[i + 1];
    uint8_t byte = strtoul(byteString, NULL, 16);
    parseByte(byte);
  }
}
```

**Note**: This modification is for testing purposes only and assumes the Arduino has enough memory to handle the string.

### Conclusion

The provided code should help you decode the UART packets from your coffee machine's DWIN DGUS screen. By parsing the packets and interpreting the data, you can monitor sensor readings like temperature in real-time.

If you have any questions or need further assistance with modifying the code to suit your specific needs, feel free to ask!


Link that might help
- https://www.dwin-global.com/development-guide/
- https://chatgpt.com/share/6747c6b6-f640-8004-90ed-9513ffe290fd

