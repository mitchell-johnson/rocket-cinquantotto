"""
Tests for the web server module.

Tests the HTTP response builders, SSE broker, and request parsing.
These run on CPython -- no MicroPython or network required.
"""

import asyncio
import json
import pytest

from uart_monitor.web_server import (
    SSEBroker, JsonEncoder,
    html_response, json_response, sse_headers, not_found_response,
    parse_request_line, DASHBOARD_HTML,
)


# ---------------------------------------------------------------------------
# HTTP response formatting
# ---------------------------------------------------------------------------

class TestHTTPResponses:

    def test_html_response_status(self):
        resp = html_response("<h1>hi</h1>")
        assert resp.startswith("HTTP/1.1 200 OK\r\n")

    def test_html_response_content_type(self):
        resp = html_response("<h1>hi</h1>")
        assert "Content-Type: text/html" in resp

    def test_html_response_body(self):
        body = "<h1>test</h1>"
        resp = html_response(body)
        assert resp.endswith(body)

    def test_html_response_content_length(self):
        body = "<h1>test</h1>"
        resp = html_response(body)
        assert ("Content-Length: %d" % len(body)) in resp

    def test_json_response_status(self):
        resp = json_response({"ok": True})
        assert resp.startswith("HTTP/1.1 200 OK\r\n")

    def test_json_response_content_type(self):
        resp = json_response({"ok": True})
        assert "Content-Type: application/json" in resp

    def test_json_response_body_is_valid_json(self):
        data = {"count": 42, "name": "test"}
        resp = json_response(data)
        body = resp.split("\r\n\r\n", 1)[1]
        parsed = json.loads(body)
        assert parsed["count"] == 42
        assert parsed["name"] == "test"

    def test_sse_headers_content_type(self):
        h = sse_headers()
        assert "text/event-stream" in h

    def test_sse_headers_no_cache(self):
        h = sse_headers()
        assert "Cache-Control: no-cache" in h

    def test_sse_headers_keep_alive(self):
        h = sse_headers()
        assert "Connection: keep-alive" in h

    def test_not_found_response(self):
        resp = not_found_response()
        assert "404" in resp
        assert "Not Found" in resp

    def test_cors_headers_present(self):
        resp = html_response("test")
        assert "Access-Control-Allow-Origin: *" in resp

    def test_cors_on_json(self):
        resp = json_response({})
        assert "Access-Control-Allow-Origin: *" in resp


# ---------------------------------------------------------------------------
# Request line parsing
# ---------------------------------------------------------------------------

class TestRequestParsing:

    def test_get_root(self):
        method, path = parse_request_line("GET / HTTP/1.1")
        assert method == "GET"
        assert path == "/"

    def test_get_events(self):
        method, path = parse_request_line("GET /events HTTP/1.1")
        assert method == "GET"
        assert path == "/events"

    def test_get_api_stats(self):
        method, path = parse_request_line("GET /api/stats HTTP/1.1")
        assert method == "GET"
        assert path == "/api/stats"

    def test_malformed_request(self):
        method, path = parse_request_line("BADREQUEST")
        assert method is None
        assert path is None

    def test_empty_string(self):
        method, path = parse_request_line("")
        assert method is None


# ---------------------------------------------------------------------------
# SSE Broker
# ---------------------------------------------------------------------------

class FakeWriter:
    """Simulates an asyncio.StreamWriter for testing."""

    def __init__(self, fail_on_write=False):
        self.data = bytearray()
        self.closed = False
        self.fail_on_write = fail_on_write

    def write(self, payload):
        if self.fail_on_write:
            raise OSError("connection reset")
        self.data.extend(payload)

    async def drain(self):
        if self.fail_on_write:
            raise OSError("connection reset")


class TestSSEBroker:

    def test_initial_state(self):
        broker = SSEBroker()
        assert broker.client_count == 0
        assert broker.total_packets == 0
        assert broker.history == []

    def test_add_remove_client(self):
        broker = SSEBroker()
        w = FakeWriter()
        broker.add_client(w)
        assert broker.client_count == 1
        broker.remove_client(w)
        assert broker.client_count == 0

    def test_remove_nonexistent_client(self):
        broker = SSEBroker()
        w = FakeWriter()
        broker.remove_client(w)  # should not raise
        assert broker.client_count == 0

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_client(self):
        broker = SSEBroker()
        w = FakeWriter()
        broker.add_client(w)

        pkt_dict = {"hex": "5AA509821041000100051654", "command": "0x82"}
        await broker.broadcast(pkt_dict)

        output = w.data.decode()
        assert output.startswith("data: ")
        assert output.endswith("\n\n")
        payload = json.loads(output[len("data: "):-2])
        assert payload["hex"] == "5AA509821041000100051654"

    @pytest.mark.asyncio
    async def test_broadcast_increments_counter(self):
        broker = SSEBroker()
        w = FakeWriter()
        broker.add_client(w)
        await broker.broadcast({"test": 1})
        await broker.broadcast({"test": 2})
        assert broker.total_packets == 2

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_clients(self):
        broker = SSEBroker()
        w1 = FakeWriter()
        w2 = FakeWriter()
        broker.add_client(w1)
        broker.add_client(w2)

        await broker.broadcast({"n": 1})
        assert len(w1.data) > 0
        assert len(w2.data) > 0
        assert w1.data == w2.data

    @pytest.mark.asyncio
    async def test_dead_client_removed(self):
        broker = SSEBroker()
        good = FakeWriter()
        bad = FakeWriter(fail_on_write=True)
        broker.add_client(good)
        broker.add_client(bad)
        assert broker.client_count == 2

        await broker.broadcast({"n": 1})
        assert broker.client_count == 1  # bad client removed
        assert len(good.data) > 0

    @pytest.mark.asyncio
    async def test_history_maintained(self):
        broker = SSEBroker(max_history=3)
        w = FakeWriter()
        broker.add_client(w)

        for i in range(5):
            await broker.broadcast({"n": i})

        assert len(broker.history) == 3
        assert broker.history[0]["n"] == 2  # oldest retained
        assert broker.history[2]["n"] == 4  # newest

    def test_total_clients_served(self):
        broker = SSEBroker()
        w1 = FakeWriter()
        w2 = FakeWriter()
        broker.add_client(w1)
        broker.add_client(w2)
        broker.remove_client(w1)
        assert broker.total_clients_served == 2
        assert broker.client_count == 1


# ---------------------------------------------------------------------------
# JSON Encoder
# ---------------------------------------------------------------------------

class TestJsonEncoder:

    def test_encode_dict(self):
        result = JsonEncoder.encode({"a": 1, "b": "hello"})
        parsed = json.loads(result)
        assert parsed["a"] == 1
        assert parsed["b"] == "hello"

    def test_encode_list(self):
        result = JsonEncoder.encode([1, 2, 3])
        assert json.loads(result) == [1, 2, 3]


# ---------------------------------------------------------------------------
# Dashboard HTML
# ---------------------------------------------------------------------------

class TestDashboardHTML:

    def test_contains_title(self):
        assert "UART Monitor" in DASHBOARD_HTML

    def test_contains_eventsource(self):
        assert "EventSource" in DASHBOARD_HTML

    def test_contains_events_endpoint(self):
        assert "/events" in DASHBOARD_HTML

    def test_is_valid_html(self):
        assert DASHBOARD_HTML.strip().startswith("<!DOCTYPE html>")
        assert "</html>" in DASHBOARD_HTML
