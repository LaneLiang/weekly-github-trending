"""QQ Bot HTTP webhook server — receives bot events and returns responses.

QQ Bot supports both WebSocket and HTTP webhook modes.
This implements the HTTP webhook mode for consistency with the existing architecture.
"""

from __future__ import annotations

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Callable

logger = logging.getLogger("lanes_ceo.qqbot_server")

EventCallback = Callable[[dict], dict | None]


def _compute_qqbot_signature(plain_token: str, event_ts: str, app_secret: str) -> str:
    """Compute QQ Bot webhook validation signature: sha256(plain_token + event_ts + app_secret)."""
    import hashlib
    raw = f"{plain_token}{event_ts}{app_secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class _QQBotHandler(BaseHTTPRequestHandler):
    """HTTP handler for QQ Bot webhook callbacks."""

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        if not body:
            self._send_json(400, {"error": "empty body"})
            return

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        # QQ Bot may send a challenge/verification payload
        opcode = payload.get("op")
        if opcode == 13:  # Validation challenge
            logger.info("QQ Bot validation challenge received")
            d = payload.get("d", {})
            plain_token = d.get("plain_token", "")
            event_ts = d.get("event_ts", "")
            app_secret = getattr(self.server, "qqbot_app_secret", "")
            signature = _compute_qqbot_signature(plain_token, event_ts, app_secret)
            self._send_json(200, {"plain_token": plain_token, "signature": signature})
            return

        # QQ Bot message event: opcode 0 = dispatch
        event_type = payload.get("t", "")
        logger.info("QQ Bot event: type=%s op=%s", event_type, opcode)

        callback = getattr(self.server, "orchestrator_callback", None)
        if callback:
            try:
                result = callback(payload)
                if result:
                    self._send_json(200, result)
                else:
                    self._send_json(200, {})
            except Exception as exc:
                logger.error("QQ Bot callback failed: %s", exc)
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

    def log_message(self, format, *args):
        logger.debug("HTTP: %s", format % args)


class QQBotServer:
    """Embeddable HTTP server for receiving QQ Bot webhook callbacks.

    Usage:
        server = QQBotServer(host="0.0.0.0", port=8082)
        server.set_callback(lambda event: handle_event(event))
        server.start()
        server.stop()
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8082, app_secret: str = "") -> None:
        self.host = host
        self.port = port
        self.app_secret = app_secret
        self._httpd: HTTPServer | None = None
        self._thread: Thread | None = None
        self._running = False

    def set_callback(self, callback: EventCallback) -> None:
        """Set the function called for each incoming QQ Bot event."""
        self._callback = callback
        if self._httpd:
            self._httpd.orchestrator_callback = callback  # type: ignore[attr-defined]

    def start(self) -> None:
        """Start the HTTP server in a background thread."""
        self._httpd = HTTPServer((self.host, self.port), _QQBotHandler)
        self._httpd.qqbot_app_secret = self.app_secret  # type: ignore[attr-defined]
        self._httpd.orchestrator_callback = getattr(self, "_callback", None)  # type: ignore[attr-defined]
        self._thread = Thread(target=self._httpd.serve_forever, daemon=True, name="qqbot-server")
        self._thread.start()
        self._running = True
        logger.info("QQ Bot webhook server started on %s:%d", self.host, self.port)

    def stop(self) -> None:
        """Shut down the HTTP server."""
        if self._httpd:
            self._httpd.shutdown()
            self._httpd = None
        self._running = False
        logger.info("QQ Bot webhook server stopped")

    @property
    def is_running(self) -> bool:
        return self._running
