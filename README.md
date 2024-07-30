# rocket-cinquantotto
Investigation into hacking the rocket cinquantotto USB UART output to export information

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
