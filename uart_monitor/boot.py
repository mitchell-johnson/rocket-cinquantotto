"""
boot.py -- runs once on MicroPython startup.

Connects to WiFi and prints the device IP so you know where to point
your browser.
"""

import network
import time

from .config import WIFI_SSID, WIFI_PASSWORD


def connect_wifi(ssid=WIFI_SSID, password=WIFI_PASSWORD, timeout_s=15):
    """Connect to WiFi, return the IP address string or raise on timeout."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("Already connected: %s" % ip)
        return ip

    print("Connecting to %s ..." % ssid)
    wlan.connect(ssid, password)

    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout_s:
            raise OSError("WiFi connection timed out after %ds" % timeout_s)
        time.sleep(0.5)
        print(".", end="")

    ip = wlan.ifconfig()[0]
    print("\nConnected!  IP: %s" % ip)
    return ip
