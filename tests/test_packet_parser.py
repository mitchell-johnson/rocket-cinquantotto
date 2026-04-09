"""
Tests for the DWIN DGUS packet parser.

Uses real packet data captured from the Rocket Espresso coffee machine.
"""

import pytest
from uart_monitor.packet_parser import (
    PacketParser, Packet, parse_hex_string,
    VALID_HEADERS, CMD_WRITE_VAR, CMD_READ_VAR,
)


# ---------------------------------------------------------------------------
# Real packets from the README / coffee.ino observations
# ---------------------------------------------------------------------------

# Common idle packet: header 5AA5, bytecount 09, cmd 82, addr 1041, data 0001 0005, checksum 1654
IDLE_PACKET_HEX = "5AA509821041000100051654"

# Variant header 5EA5
VARIANT_5EA5_HEX = "5EA509821041000100051654"

# Variant header 5AA7
VARIANT_5AA7_HEX = "5AA709821041000100058BF5"

# Different address with larger data
PACKET_8001_HEX = "5AA5098210418001004111FF"


class TestPacketParserBasic:
    """Test basic parser operations."""

    def test_parse_single_packet(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        assert pkt is not None
        assert pkt.header == (0x5A, 0xA5)
        assert pkt.byte_count == 9
        assert pkt.command == CMD_WRITE_VAR
        assert pkt.address == 0x1041

    def test_hex_string_roundtrip(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        assert pkt.hex_string() == IDLE_PACKET_HEX

    def test_data_words_parsed(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        # After address (1041), remaining bytes: 00 01 00 05 16 54
        # These are 3 words: 0x0001, 0x0005, 0x1654
        assert len(pkt.data_words) >= 2
        assert pkt.data_words[0] == 0x0001
        assert pkt.data_words[1] == 0x0005

    def test_to_dict_format(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        d = pkt.to_dict()
        assert d["hex"] == IDLE_PACKET_HEX
        assert d["header"] == "5AA5"
        assert d["command"] == "0x82"
        assert d["address"] == "0x1041"
        assert isinstance(d["data_words"], list)
        assert d["byte_count"] == 9


class TestVariantHeaders:
    """Test that all valid DWIN header variants are recognized."""

    def test_header_5ea5(self):
        pkt = parse_hex_string(VARIANT_5EA5_HEX)
        assert pkt is not None
        assert pkt.header == (0x5E, 0xA5)
        assert pkt.command == CMD_WRITE_VAR
        assert pkt.address == 0x1041

    def test_header_5aa7(self):
        pkt = parse_hex_string(VARIANT_5AA7_HEX)
        assert pkt is not None
        assert pkt.header == (0x5A, 0xA7)
        assert pkt.command == CMD_WRITE_VAR
        assert pkt.address == 0x1041

    def test_all_valid_headers_defined(self):
        assert (0x5A, 0xA5) in VALID_HEADERS
        assert (0x5E, 0xA5) in VALID_HEADERS
        assert (0x5A, 0xA7) in VALID_HEADERS
        assert (0x5E, 0xA7) in VALID_HEADERS


class TestStreamParsing:
    """Test the stateful stream parser with chunked / concatenated input."""

    def test_two_packets_concatenated(self):
        """Parser should extract both packets from a continuous stream."""
        combined = bytes.fromhex(IDLE_PACKET_HEX + VARIANT_5EA5_HEX)
        parser = PacketParser()
        packets = parser.feed(combined)
        assert len(packets) == 2
        assert packets[0].header == (0x5A, 0xA5)
        assert packets[1].header == (0x5E, 0xA5)

    def test_byte_at_a_time(self):
        """Parser should work when fed one byte at a time."""
        raw = bytes.fromhex(IDLE_PACKET_HEX)
        parser = PacketParser()
        packets = []
        for b in raw:
            packets.extend(parser.feed(bytes([b])))
        assert len(packets) == 1
        assert packets[0].hex_string() == IDLE_PACKET_HEX

    def test_garbage_before_packet(self):
        """Parser should skip garbage bytes before a valid header."""
        garbage = b"\x00\xFF\x12\x34"
        raw = garbage + bytes.fromhex(IDLE_PACKET_HEX)
        parser = PacketParser()
        packets = parser.feed(raw)
        assert len(packets) == 1
        assert packets[0].hex_string() == IDLE_PACKET_HEX

    def test_split_across_feeds(self):
        """Packet split across two feed() calls should still parse."""
        raw = bytes.fromhex(IDLE_PACKET_HEX)
        mid = len(raw) // 2
        parser = PacketParser()
        p1 = parser.feed(raw[:mid])
        p2 = parser.feed(raw[mid:])
        all_packets = p1 + p2
        assert len(all_packets) == 1
        assert all_packets[0].hex_string() == IDLE_PACKET_HEX

    def test_multiple_packets_with_garbage_between(self):
        """Handles garbage between valid packets."""
        raw = (bytes.fromhex(IDLE_PACKET_HEX)
               + b"\xFF\xFF\xFF"
               + bytes.fromhex(VARIANT_5EA5_HEX))
        parser = PacketParser()
        packets = parser.feed(raw)
        assert len(packets) == 2

    def test_empty_feed(self):
        parser = PacketParser()
        assert parser.feed(b"") == []

    def test_incomplete_packet_no_output(self):
        """Incomplete data should not produce a packet."""
        raw = bytes.fromhex(IDLE_PACKET_HEX)
        parser = PacketParser()
        packets = parser.feed(raw[:5])  # only 5 of 12 bytes
        assert len(packets) == 0


class TestEdgeCases:
    """Edge cases and robustness checks."""

    def test_invalid_header_skipped(self):
        """A byte sequence that almost looks like a header is skipped."""
        bad = b"\x5A\x00"  # 5A but not followed by A5/A7
        raw = bad + bytes.fromhex(IDLE_PACKET_HEX)
        parser = PacketParser()
        packets = parser.feed(raw)
        assert len(packets) == 1
        assert packets[0].header == (0x5A, 0xA5)

    def test_zero_byte_count_skipped(self):
        """A header followed by byte_count=0 should be discarded (invalid)."""
        # Header + byte_count=0 means packet_length=3, which is < MIN_PACKET_SIZE
        bad = b"\x5A\xA5\x00"
        raw = bad + bytes.fromhex(IDLE_PACKET_HEX)
        parser = PacketParser()
        packets = parser.feed(raw)
        assert len(packets) == 1

    def test_timestamp_propagated(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX, timestamp_ms=42000)
        assert pkt.timestamp_ms == 42000
        assert pkt.to_dict()["timestamp_ms"] == 42000

    def test_parse_hex_string_with_spaces(self):
        spaced = "5A A5 09 82 10 41 00 01 00 05 16 54"
        pkt = parse_hex_string(spaced)
        assert pkt is not None
        assert pkt.hex_string() == IDLE_PACKET_HEX

    def test_parse_hex_string_invalid(self):
        """Totally invalid data returns None."""
        assert parse_hex_string("DEADBEEF") is None

    def test_different_address_packet(self):
        pkt = parse_hex_string(PACKET_8001_HEX)
        assert pkt is not None
        assert pkt.address == 0x1041
        assert pkt.command == CMD_WRITE_VAR

    def test_large_stream(self):
        """Parser handles many packets in a row without issues."""
        raw = bytes.fromhex(IDLE_PACKET_HEX) * 100
        parser = PacketParser()
        packets = parser.feed(raw)
        assert len(packets) == 100
        for p in packets:
            assert p.hex_string() == IDLE_PACKET_HEX

    def test_buffer_overflow_recovery(self):
        """Parser recovers after its internal buffer overflows."""
        parser = PacketParser(buffer_size=16)  # tiny buffer
        # Feed garbage to fill it up
        parser.feed(b"\xFF" * 20)
        # Then feed a real packet
        packets = parser.feed(bytes.fromhex(IDLE_PACKET_HEX))
        assert len(packets) == 1


class TestPacketObject:
    """Test Packet methods and properties."""

    def test_slots_defined(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        assert hasattr(pkt, "__slots__")

    def test_hex_string_uppercase(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX.lower())
        assert pkt.hex_string() == IDLE_PACKET_HEX

    def test_to_dict_keys(self):
        pkt = parse_hex_string(IDLE_PACKET_HEX)
        d = pkt.to_dict()
        expected_keys = {"hex", "header", "command", "address",
                         "data_words", "byte_count", "timestamp_ms"}
        assert set(d.keys()) == expected_keys
