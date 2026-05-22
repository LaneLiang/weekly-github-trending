"""Feishu/Lark HTTP webhook server — receives bot events and returns responses.

Flow:
  User sends message in Feishu group
  → Feishu sends HTTP POST to our webhook URL
  → FeishuServer receives event, HermesFeishuAdapter parses into TaskRequest
  → Orchestrator orchestrates the workflow
  → FeishuSender sends the result back to the group chat

Feishu event subscription requires:
  - URL verification (challenge) on first setup
  - Message receive events (im.message.receive_v1)
"""

from __future__ import annotations

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Callable

from lanes_ceo.ingress.hermes import HermesFeishuAdapter

logger = logging.getLogger("lanes_ceo.feishu_server")

EventCallback = Callable[[dict], dict | None]


class _FeishuHandler(BaseHTTPRequestHandler):
    """HTTP handler for Feishu event callbacks."""

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.server.rfile.read(content_length) if content_length else b""
        if not body:
            self._send_json(400, {"error": "empty body"})
            return

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        event_type = payload.get("header", {}).get("event_type", "")
        logger.info("Feishu event received: type=%s", event_type)

        # ── URL verification challenge ──
        challenge = payload.get("challenge")
        if challenge:
            logger.info("Feishu URL verification challenge received")
            token = payload.get("token", "")
            self._send_json(200, {"challenge": challenge})
            return

        # ── Route to orchestrator callback ──
        callback = getattr(self.server, "orchestrator_callback", None)
        if callback:
            try:
                result = callback(payload)
                if result:
                    self._send_json(200, result)
                else:
                    self._send_json(200, {})
            except Exception as exc:
                logger.error("Orchestrator callback failed: %s", exc)
                self._send_json(500, {"error": str(exc)})
        else:
            self._send_json(200, {})

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Suppress default request logging noise
    def log_message(self, format, *args):
        logger.debug("HTTP: %s", format % args)


class FeishuServer:
    """Embeddable HTTP server for receiving Feishu event callbacks.

    Usage:
        server = FeishuServer(host="0.0.0.0", port=8080)
        server.set_callback(lambda event: handle_event(event))
        server.start()
        # ... later ...
        server.stop()
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self._httpd: HTTPServer | None = None
        self._thread: Thread | None = None
        self._running = False

    def set_callback(self, callback: EventCallback) -> None:
        """Set the function called for each incoming Feishu event."""
        self._callback = callback
        if self._httpd:
            self._httpd.orchestrator_callback = callback  # type: ignore[attr-defined]

    def start(self) -> None:
        """Start the HTTP server in a background thread."""
        self._httpd = HTTPServer((self.host, self.port), _FeishuHandler)
        self._httpd.orchestrator_callback = getattr(self, "_callback", None)  # type: ignore[attr-defined]
        self._thread = Thread(target=self._httpd.serve_forever, daemon=True, name="feishu-server")
        self._thread.start()
        self._running = True
        logger.info("Feishu webhook server started on %s:%d", self.host, self.port)

    def stop(self) -> None:
        """Shut down the HTTP server."""
        if self._httpd:
            self._httpd.shutdown()
            self._httpd = None
        self._running = False
        logger.info("Feishu webhook server stopped")

    @property
    def is_running(self) -> bool:
        return self._running
