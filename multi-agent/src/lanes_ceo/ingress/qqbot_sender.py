"""QQ Bot message sender — sends messages via QQ Bot HTTP API.

Uses the QQ Bot Open API to send text and markdown messages.
QQ Bot is available for both group and private chat scenarios.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from lanes_ceo.ingress.shared import json_dumps, json_loads

logger = logging.getLogger("lanes_ceo.qqbot_sender")


@dataclass
class QQBotConfig:
    app_id: str
    app_secret: str


class QQBotSender:
    """Sends messages via QQ Bot HTTP API.

    Uses pure urllib.request — no third-party QQ SDK needed.
    """

    def __init__(self, config: QQBotConfig) -> None:
        self.app_id = config.app_id
        self.app_secret = config.app_secret
        self._access_token: str | None = None
        self._token_expire_time: float = 0

    def send_text(self, openid: str, text: str) -> bool:
        """Send a plain text message to a QQ user or group channel."""
        return self._send_message(openid, "text", {"content": text})

    def send_markdown(self, openid: str, content: str) -> bool:
        """Send a markdown message to a QQ user or group channel."""
        return self._send_message(openid, "markdown", {"content": content})

    # ── internal ──

    def _send_message(self, openid: str, msg_type: str, payload: dict) -> bool:
        token = self._get_access_token()
        if not token:
            return False

        import urllib.request

        body = json_dumps({
            "msg_type": msg_type,
            "content": json_dumps(payload),
            "msg_id": "",
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"https://api.sgroup.qq.com/v2/users/{openid}/messages",
                data=body,
                headers={
                    "Authorization": f"QQBot {token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                code = data.get("code", -1)
                if code != 0:
                    logger.error("QQ Bot send failed: code=%s msg=%s",
                                 code, data.get("message", ""))
                    return False
                return True
        except Exception as exc:
            logger.error("QQ Bot send exception: %s", exc)
            return False

    def _get_access_token(self) -> str | None:
        """Get a valid QQ Bot access token, refreshing if expired."""
        import time
        import urllib.request

        if self._access_token and time.time() < self._token_expire_time:
            return self._access_token

        body = json_dumps({
            "appId": self.app_id,
            "clientSecret": self.app_secret,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                "https://bots.qq.com/app/getAppAccessToken",
                data=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                token = data.get("access_token", "")
                if not token:
                    logger.error("Failed to get QQ Bot access token: %s", data)
                    return None
                expires_in = data.get("expires_in", 7200)
                self._access_token = token
                self._token_expire_time = time.time() + expires_in - 300
                logger.info("QQ Bot access token refreshed, expires in %ds", expires_in)
                return token
        except Exception as exc:
            logger.error("QQ Bot access token exception: %s", exc)
            return None


