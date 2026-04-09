"""
Async HTTP server with Server-Sent Events (SSE) for streaming UART packets.

Designed for MicroPython on ESP32-S3 (LOLIN S3).
Uses uasyncio (aliased as asyncio) for cooperative multitasking.

Endpoints:
  GET /          - Dashboard HTML page (live packet viewer)
  GET /events    - SSE stream of parsed UART packets (application/json per event)
  GET /api/stats - JSON snapshot of current stats
"""

try:
    import uasyncio as asyncio
    import ujson as json
except ImportError:
    import asyncio
    import json


# -- SSE Client Registry -----------------------------------------------------

class JsonEncoder:
    """Minimal JSON encoder that handles Packet.to_dict() output."""

    @staticmethod
    def encode(obj):
        return json.dumps(obj)


class SSEBroker:
    """Fan-out broker: packets are pushed to all connected SSE clients."""

    def __init__(self, max_history=50):
        self._clients = []       # list of asyncio.StreamWriter
        self._history = []       # ring buffer of recent events
        self._max_history = max_history
        self.total_packets = 0
        self.total_clients_served = 0

    def add_client(self, writer):
        self._clients.append(writer)
        self.total_clients_served += 1

    def remove_client(self, writer):
        try:
            self._clients.remove(writer)
        except ValueError:
            pass

    @property
    def client_count(self):
        return len(self._clients)

    @property
    def history(self):
        return list(self._history)

    async def broadcast(self, packet_dict):
        """Send a packet dict to every connected SSE client."""
        self.total_packets += 1
        payload = "data: %s\n\n" % JsonEncoder.encode(packet_dict)
        payload_bytes = payload.encode()

        self._history.append(packet_dict)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        dead = []
        for writer in self._clients:
            try:
                writer.write(payload_bytes)
                await writer.drain()
            except Exception:
                dead.append(writer)

        for w in dead:
            self.remove_client(w)


# -- HTTP Response Helpers ----------------------------------------------------

HTTP_200 = "HTTP/1.1 200 OK\r\n"
HTTP_404 = "HTTP/1.1 404 Not Found\r\n"

CORS_HEADERS = "Access-Control-Allow-Origin: *\r\n"


def html_response(body):
    """Build a complete HTTP response for HTML content."""
    return (
        HTTP_200
        + "Content-Type: text/html; charset=utf-8\r\n"
        + CORS_HEADERS
        + "Connection: close\r\n"
        + "Content-Length: %d\r\n" % len(body)
        + "\r\n"
        + body
    )


def json_response(obj):
    """Build a complete HTTP response for JSON content."""
    body = JsonEncoder.encode(obj)
    return (
        HTTP_200
        + "Content-Type: application/json\r\n"
        + CORS_HEADERS
        + "Connection: close\r\n"
        + "Content-Length: %d\r\n" % len(body)
        + "\r\n"
        + body
    )


def sse_headers():
    """Return headers that begin an SSE stream (no body -- body is streamed)."""
    return (
        HTTP_200
        + "Content-Type: text/event-stream\r\n"
        + "Cache-Control: no-cache\r\n"
        + CORS_HEADERS
        + "Connection: keep-alive\r\n"
        + "\r\n"
    )


def not_found_response():
    body = "404 Not Found"
    return (
        HTTP_404
        + "Content-Type: text/plain\r\n"
        + "Connection: close\r\n"
        + "Content-Length: %d\r\n" % len(body)
        + "\r\n"
        + body
    )


# -- Dashboard HTML -----------------------------------------------------------

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UART Monitor - Rocket Espresso</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Courier New', monospace; background: #1a1a2e; color: #e0e0e0; padding: 1rem; }
  h1 { color: #e94560; margin-bottom: .5rem; font-size: 1.4rem; }
  .status { padding: .3rem .6rem; border-radius: 4px; font-size: .85rem; display: inline-block; margin-bottom: 1rem; }
  .status.connected { background: #0f3d0f; color: #4caf50; }
  .status.disconnected { background: #3d0f0f; color: #f44336; }
  .stats { font-size: .8rem; color: #888; margin-bottom: .5rem; }
  #packets { max-height: 80vh; overflow-y: auto; }
  .pkt { background: #16213e; border-left: 3px solid #e94560; padding: .4rem .6rem;
         margin-bottom: 2px; font-size: .82rem; display: flex; gap: 1rem; flex-wrap: wrap; }
  .pkt .hex { color: #0f9b58; word-break: break-all; }
  .pkt .cmd { color: #e94560; }
  .pkt .addr { color: #4fc3f7; }
  .pkt .data { color: #fff176; }
  .pkt .ts { color: #666; min-width: 6em; }
  .controls { margin-bottom: .5rem; }
  button { background: #e94560; color: #fff; border: none; padding: .3rem .8rem;
           border-radius: 3px; cursor: pointer; font-family: inherit; margin-right: .3rem; }
  button:hover { background: #c73650; }
</style>
</head>
<body>
<h1>UART Monitor</h1>
<span id="status" class="status disconnected">Disconnected</span>
<div class="stats">Packets: <span id="count">0</span> | Clients: <span id="clients">-</span></div>
<div class="controls">
  <button onclick="clearPackets()">Clear</button>
  <button onclick="toggleAutoScroll()">Auto-scroll: ON</button>
</div>
<div id="packets"></div>
<script>
let count = 0, autoScroll = true;
const el = document.getElementById('packets');
const statusEl = document.getElementById('status');
const countEl = document.getElementById('count');

function toggleAutoScroll() {
  autoScroll = !autoScroll;
  event.target.textContent = 'Auto-scroll: ' + (autoScroll ? 'ON' : 'OFF');
}
function clearPackets() { el.innerHTML = ''; count = 0; countEl.textContent = '0'; }

function connect() {
  const es = new EventSource('/events');
  es.onopen = () => { statusEl.textContent = 'Connected'; statusEl.className = 'status connected'; };
  es.onerror = () => {
    statusEl.textContent = 'Disconnected'; statusEl.className = 'status disconnected';
    es.close(); setTimeout(connect, 2000);
  };
  es.onmessage = (e) => {
    const p = JSON.parse(e.data);
    count++;
    countEl.textContent = count;
    const div = document.createElement('div');
    div.className = 'pkt';
    div.innerHTML =
      '<span class="ts">' + p.timestamp_ms + 'ms</span>' +
      '<span class="cmd">' + (p.command || '') + '</span>' +
      '<span class="addr">' + (p.address || '') + '</span>' +
      '<span class="data">' + (p.data_words ? p.data_words.join(' ') : '') + '</span>' +
      '<span class="hex">' + p.hex + '</span>';
    el.appendChild(div);
    if (el.children.length > 500) el.removeChild(el.firstChild);
    if (autoScroll) div.scrollIntoView({behavior: 'smooth'});
  };
}
connect();
</script>
</body>
</html>
"""


# -- Request Router -----------------------------------------------------------

def parse_request_line(raw_line):
    """Extract method and path from an HTTP request line."""
    parts = raw_line.split(" ")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


async def handle_client(reader, writer, broker):
    """Handle a single HTTP connection."""
    try:
        line = await asyncio.wait_for(reader.readline(), timeout=5.0)
        if not line:
            writer.close()
            await writer.wait_closed()
            return

        request_line = line.decode().strip()
        method, path = parse_request_line(request_line)

        # consume remaining headers
        while True:
            header_line = await asyncio.wait_for(reader.readline(), timeout=5.0)
            if header_line in (b"\r\n", b"\n", b""):
                break

        if path == "/":
            resp = html_response(DASHBOARD_HTML)
            writer.write(resp.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        elif path == "/events":
            writer.write(sse_headers().encode())
            await writer.drain()
            # replay recent history
            for pkt_dict in broker.history:
                payload = "data: %s\n\n" % JsonEncoder.encode(pkt_dict)
                writer.write(payload.encode())
                await writer.drain()
            broker.add_client(writer)
            # keep connection open -- broker will write events

        elif path == "/api/stats":
            stats = {
                "total_packets": broker.total_packets,
                "connected_clients": broker.client_count,
                "total_clients_served": broker.total_clients_served,
                "history_size": len(broker.history),
            }
            resp = json_response(stats)
            writer.write(resp.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        else:
            resp = not_found_response()
            writer.write(resp.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    except Exception:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def start_server(broker, host="0.0.0.0", port=80):
    """Start the HTTP server. Returns the asyncio.Server object."""

    async def _handler(reader, writer):
        await handle_client(reader, writer, broker)

    server = await asyncio.start_server(_handler, host, port)
    print("Web server listening on http://%s:%d" % (host, port))
    return server
