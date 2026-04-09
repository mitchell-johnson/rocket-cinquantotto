"""
DWIN DGUS UART packet parser.

Parses packets from the Rocket Espresso coffee machine's DWIN DGUS display.
Pure Python -- no hardware dependencies, runs on MicroPython and CPython.

Packet format (from coffee.ino / protocol spec):
  - Header:     2 bytes (0x5A 0xA5 primary; 0x5E 0xA5, 0x5A 0xA7, 0x5E 0xA7 also valid)
  - Byte count:  1 byte  (number of bytes that follow)
  - Payload:     <byte_count> bytes (command + address + data + optional checksum)
  Total length = 3 + byte_count
"""

VALID_HEADERS = frozenset([
    (0x5A, 0xA5),
    (0x5E, 0xA5),
    (0x5A, 0xA7),
    (0x5E, 0xA7),
])

CMD_WRITE_VAR = 0x82
CMD_READ_VAR = 0x83

# Minimum: header(2) + byte_count(1) + command(1)
MIN_PACKET_SIZE = 4


class Packet:
    """Represents a parsed DWIN DGUS packet."""

    __slots__ = ("header", "byte_count", "command", "address", "data_words",
                 "raw", "timestamp_ms")

    def __init__(self, header, byte_count, command, address, data_words,
                 raw, timestamp_ms=0):
        self.header = header
        self.byte_count = byte_count
        self.command = command
        self.address = address
        self.data_words = data_words  # list of 16-bit ints
        self.raw = raw                # original bytes
        self.timestamp_ms = timestamp_ms

    def hex_string(self):
        """Return the packet as an uppercase hex string."""
        return "".join("%02X" % b for b in self.raw)

    def to_dict(self):
        """Serialize for JSON / SSE transmission."""
        return {
            "hex": self.hex_string(),
            "header": "%02X%02X" % (self.header[0], self.header[1]),
            "command": "0x%02X" % self.command,
            "address": "0x%04X" % self.address if self.address is not None else None,
            "data_words": ["0x%04X" % w for w in self.data_words],
            "byte_count": self.byte_count,
            "timestamp_ms": self.timestamp_ms,
        }


class PacketParser:
    """
    Stateful stream parser.  Feed it bytes one-at-a-time or in chunks;
    it yields complete Packet objects as they are detected.
    """

    def __init__(self, buffer_size=512):
        self._buf = bytearray(buffer_size)
        self._idx = 0
        self._buf_size = buffer_size

    def _reset(self):
        self._idx = 0

    def feed(self, data, timestamp_ms=0):
        """
        Feed raw bytes into the parser.

        Returns a list of Packet objects parsed from the data.
        """
        packets = []
        for b in data:
            if self._idx < self._buf_size:
                self._buf[self._idx] = b
                self._idx += 1
            else:
                # overflow -- drop oldest byte and shift
                self._shift_one()
                self._buf[self._idx] = b
                self._idx += 1

            pkt = self._try_parse(timestamp_ms)
            if pkt is not None:
                packets.append(pkt)
        return packets

    def _shift_one(self):
        """Remove the first byte, shift everything left."""
        for i in range(1, self._idx):
            self._buf[i - 1] = self._buf[i]
        self._idx -= 1

    def _try_parse(self, timestamp_ms):
        """Check if the buffer contains a complete valid packet at index 0."""
        while self._idx >= MIN_PACKET_SIZE:
            h = (self._buf[0], self._buf[1])
            if h not in VALID_HEADERS:
                # not a valid header -- drop first byte and retry
                self._shift_one()
                continue

            byte_count = self._buf[2]
            packet_length = 3 + byte_count

            if packet_length < MIN_PACKET_SIZE:
                # nonsensical byte_count -- drop header and retry
                self._shift_one()
                continue

            if self._idx < packet_length:
                # need more bytes
                return None

            raw = bytes(self._buf[:packet_length])
            pkt = self._parse_packet(raw, timestamp_ms)

            # consume the packet from the buffer
            remaining = self._idx - packet_length
            for i in range(remaining):
                self._buf[i] = self._buf[packet_length + i]
            self._idx = remaining

            return pkt

        return None

    @staticmethod
    def _parse_packet(raw, timestamp_ms):
        """Parse a raw byte sequence into a Packet."""
        header = (raw[0], raw[1])
        byte_count = raw[2]
        command = raw[3]

        address = None
        data_words = []

        if command == CMD_WRITE_VAR and len(raw) >= 6:
            address = (raw[4] << 8) | raw[5]
            # remaining payload after command(1) + address(2) = byte_count - 3
            data_start = 6
            data_end = 3 + byte_count  # might include checksum at the end
            payload = raw[data_start:data_end]
            # parse 16-bit words from the data portion
            i = 0
            while i + 1 < len(payload):
                word = (payload[i] << 8) | payload[i + 1]
                data_words.append(word)
                i += 2
        elif command == CMD_READ_VAR and len(raw) >= 6:
            address = (raw[4] << 8) | raw[5]

        return Packet(
            header=header,
            byte_count=byte_count,
            command=command,
            address=address,
            data_words=data_words,
            raw=raw,
            timestamp_ms=timestamp_ms,
        )


def parse_hex_string(hex_str, timestamp_ms=0):
    """Convenience: parse a single hex-encoded packet string, return a Packet or None."""
    hex_str = hex_str.strip().replace(" ", "")
    data = bytes.fromhex(hex_str) if hasattr(bytes, "fromhex") else _fromhex(hex_str)
    parser = PacketParser()
    packets = parser.feed(data, timestamp_ms)
    return packets[0] if packets else None


def _fromhex(s):
    """Fallback hex decoder for MicroPython versions lacking bytes.fromhex."""
    out = bytearray(len(s) // 2)
    for i in range(0, len(s), 2):
        out[i // 2] = int(s[i:i + 2], 16)
    return bytes(out)
