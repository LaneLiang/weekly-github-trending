"""WeChat Official Account HTTP server — receives callbacks and returns responses.

WeChat message flow:
  1. GET request: URL verification with signature/timestamp/nonce/echostr
  2. POST request: XML message body from WeChat server

WeChat's verification requires a configured Token (not the same as access_token).
The server computes sha1(sort([token, timestamp, nonce])) and compares to signature.
"""

from __future__ import annotations

import hashlib
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Callable
from xml.etree import ElementTree

logger = logging.getLogger("lanes_ceo.weixin_server")

EventCallback = Callable[[dict], dict | None]


class _WeixinHandler(BaseHTTPRequestHandler):
    """HTTP handler for WeChat Official Account callbacks."""

    def do_GET(self) -> None:
        """Handle WeChat URL verification (echostr challenge)."""
        parsed = self._parse_query()
        signature = parsed.get("signature", "")
        timestamp = parsed.get("timestamp", "")
        nonce = parsed.get("nonce", "")
        echostr = parsed.get("echostr", "")

        token = getattr(self.server, "weixin_token", "")
        if not token:
            self._send_text(403, "token not configured")
            return

        if not self._verify_signature(token, timestamp, nonce, signature):
            logger.warning("Weixin signature verification failed")
            self._send_text(403, "signature verification failed")
            return

        logger.info("Weixin URL verification passed")
        self._send_text(200, echostr)

    def do_POST(self) -> None:
        """Handle WeChat message push (XML body)."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        if not body:
            self._send_text(400, "empty body")
            return

        # Verify signature on POST messages (prevents forged message injection)
        token = getattr(self.server, "weixin_token", "")
        if token:
            parsed = self._parse_query()
            post_sig = parsed.get("signature", "")
            post_ts = parsed.get("timestamp", "")
            post_nonce = parsed.get("nonce", "")
            if not self._verify_signature(token, post_ts, post_nonce, post_sig):
                logger.warning("Weixin POST signature verification failed")
                self._send_text(403, "signature verification failed")
                return

        try:
            event = _parse_xml_message(body)
        except Exception as exc:
            logger.error("Failed to parse Weixin XML: %s", exc)
            self._send_text(200, "success")  # Always 200 to WeChat
            return

        msg_type = event.get("MsgType", "")
        logger.info("Weixin event: type=%s from=%s", msg_type, event.get("FromUserName", ""))

        callback = getattr(self.server, "orchestrator_callback", None)
        if callback:
            try:
                result = callback(event)
                if result is not None and isinstance(result, dict):
                    reply_xml = _build_text_reply(
                        event.get("FromUserName", ""),
                        event.get("ToUserName", ""),
                        result.get("text", ""),
                    )
                    self._send_xml(200, reply_xml)
                    return
            except Exception as exc:
                logger.error("Weixin callback failed: %s", exc)

        # Default: empty response (success, no reply)
        self._send_text(200, "success")

    def _verify_signature(self, token: str, timestamp: str, nonce: str, signature: str) -> bool:
        """Verify WeChat signature: sha1(sort([token, timestamp, nonce]))."""
        tmp_list = sorted([token, timestamp, nonce])
        tmp_str = "".join(tmp_list)
        computed = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()
        return computed == signature

    def _parse_query(self) -> dict[str, str]:
        """Parse query string from the request path."""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        return {k: v[0] for k, v in params.items()}

    def _send_text(self, status: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_xml(self, status: int, xml_str: str) -> None:
        body = xml_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        logger.debug("HTTP: %s", format % args)


def _parse_xml_message(body: bytes) -> dict[str, str]:
    """Parse WeChat XML message into a flat dict."""
    root = ElementTree.fromstring(body)
    result: dict[str, str] = {}
    for child in root:
        result[child.tag] = child.text or ""
    return result


def _build_text_reply(to_user: str, from_user: str, content: str) -> str:
    """Build a WeChat text reply XML."""
    import time
    return (
        "<xml>"
        f"<ToUserName><![CDATA[{to_user}]]></ToUserName>"
        f"<FromUserName><![CDATA[{from_user}]]></FromUserName>"
        f"<CreateTime>{int(time.time())}</CreateTime>"
        "<MsgType><![CDATA[text]]></MsgType>"
        f"<Content><![CDATA[{content}]]></Content>"
        "</xml>"
    )


class WeixinServer:
    """Embeddable HTTP server for receiving WeChat Official Account callbacks.

    Usage:
        server = WeixinServer(host="0.0.0.0", port=8081, token="my_wechat_token")
        server.set_callback(lambda event: handle_event(event))
        server.start()
        server.stop()
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8081, token: str = "") -> None:
        self.host = host
        self.port = port
        self.token = token
        self._httpd: HTTPServer | None = None
        self._thread: Thread | None = None
        self._running = False

    def set_callback(self, callback: EventCallback) -> None:
        """Set the function called for each incoming Weixin event."""
        self._callback = callback
        if self._httpd:
            self._httpd.orchestrator_callback = callback  # type: ignore[attr-defined]

    def start(self) -> None:
        """Start the HTTP server in a background thread."""
        self._httpd = HTTPServer((self.host, self.port), _WeixinHandler)
        self._httpd.weixin_token = self.token  # type: ignore[attr-defined]
        self._httpd.orchestrator_callback = getattr(self, "_callback", None)  # type: ignore[attr-defined]
        self._thread = Thread(target=self._httpd.serve_forever, daemon=True, name="weixin-server")
        self._thread.start()
        self._running = True
        logger.info("Weixin webhook server started on %s:%d", self.host, self.port)

    def stop(self) -> None:
        """Shut down the HTTP server."""
        if self._httpd:
            self._httpd.shutdown()
            self._httpd = None
        self._running = False
        logger.info("Weixin webhook server stopped")

    @property
    def is_running(self) -> bool:
        return self._running
