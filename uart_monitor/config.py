"""
Configuration for the UART web monitor.

Copy this file or edit in place with your network and pin settings.
"""

# -- WiFi ---------------------------------------------------------------------
WIFI_SSID = "YOUR_SSID"
WIFI_PASSWORD = "YOUR_PASSWORD"

# -- UART (LOLIN D32 Pro) ----------------------------------------------------
# The DWIN display communicates at 115200 8N1.
# D32 Pro uses ESP32-WROVER -- GPIO 16/17 are reserved for PSRAM.
# Defaults match the original coffee.ino wiring (RX=2, TX=15).
UART_ID = 1             # UART peripheral number (1 or 2 on ESP32)
UART_BAUD = 115200
UART_TX_PIN = 15        # GPIO pin for TX (to display RX)
UART_RX_PIN = 2         # GPIO pin for RX (from display TX)

# -- Web Server ---------------------------------------------------------------
WEB_PORT = 80

# -- Reader -------------------------------------------------------------------
UART_POLL_MS = 20       # how often to check the UART buffer (ms)
