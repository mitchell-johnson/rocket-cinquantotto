"""
Async UART reader for MicroPython on ESP32-S3 (LOLIN S3).

Reads bytes from the hardware UART, feeds them into PacketParser,
and broadcasts parsed packets to the SSE broker.
"""

try:
    import uasyncio as asyncio
    import utime as time
except ImportError:
    import asyncio
    import time

from .packet_parser import PacketParser


def _ticks_ms():
    """Return millisecond ticks, compatible with both MicroPython and CPython."""
    try:
        return time.ticks_ms()
    except AttributeError:
        return int(time.time() * 1000)


class UARTReader:
    """
    Continuously reads from a UART and pushes parsed packets to an SSE broker.

    Parameters:
        uart       - A MicroPython machine.UART object (or any object with
                     .any() and .read() methods).
        broker     - An SSEBroker instance from web_server.py.
        poll_ms    - How often to poll the UART (milliseconds).
    """

    def __init__(self, uart, broker, poll_ms=20):
        self.uart = uart
        self.broker = broker
        self.poll_ms = poll_ms
        self.parser = PacketParser()
        self.running = False

    async def run(self):
        """Main loop: poll UART, parse packets, broadcast."""
        self.running = True
        print("UART reader started (poll every %d ms)" % self.poll_ms)

        while self.running:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    ts = _ticks_ms()
                    packets = self.parser.feed(data, timestamp_ms=ts)
                    for pkt in packets:
                        await self.broker.broadcast(pkt.to_dict())
            await asyncio.sleep_ms(self.poll_ms)

    def stop(self):
        self.running = False
