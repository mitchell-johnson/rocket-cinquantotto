"""
main.py -- entry point for the UART web monitor.

Wires together: WiFi -> UART reader -> packet parser -> SSE web server.

Upload the entire uart_monitor/ directory to your LOLIN D32 Pro and
this will run automatically after boot.py connects to WiFi.
"""

try:
    import uasyncio as asyncio
    from machine import UART, Pin
except ImportError:
    raise SystemExit("This module must run on MicroPython (ESP32).")

from .config import (UART_ID, UART_BAUD, UART_TX_PIN, UART_RX_PIN,
                     WEB_PORT, UART_POLL_MS)
from .boot import connect_wifi
from .web_server import SSEBroker, start_server
from .uart_reader import UARTReader


def main():
    # 1. Connect to WiFi
    ip = connect_wifi()

    # 2. Set up UART
    uart = UART(UART_ID, baudrate=UART_BAUD, tx=Pin(UART_TX_PIN),
                rx=Pin(UART_RX_PIN), bits=8, parity=None, stop=1)
    print("UART%d configured: %d baud, TX=GPIO%d, RX=GPIO%d"
          % (UART_ID, UART_BAUD, UART_TX_PIN, UART_RX_PIN))

    # 3. Create broker + reader
    broker = SSEBroker()
    reader = UARTReader(uart, broker, poll_ms=UART_POLL_MS)

    # 4. Start everything concurrently
    async def _run():
        await start_server(broker, host="0.0.0.0", port=WEB_PORT)
        print("Open http://%s:%d in your browser" % (ip, WEB_PORT))
        await reader.run()

    asyncio.run(_run())


main()
