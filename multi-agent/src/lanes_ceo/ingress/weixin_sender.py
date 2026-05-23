"""WeChat Official Account message sender.

Uses the WeChat Official Account API to:
  - Send text messages via customer service API
  - Send news (article) messages
  - Manage access_token with auto-refresh
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from lanes_ceo.ingress.shared import json_dumps, json_loads

logger = logging.getLogger("lanes_ceo.weixin_sender")


@dataclass
class WeixinConfig:
    app_id: str
    app_secret: str
    token: str = ""  # Server-side verification token (not access_token)


class WeixinSender:
    """Sends messages to WeChat users via the Official Account API.

    Uses pure urllib.request — no third-party WeChat SDK needed.
    """

    def __init__(self, config: WeixinConfig) -> None:
        self.app_id = config.app_id
        self.app_secret = config.app_secret
        self._access_token: str | None = None
        self._token_expire_time: float = 0

    def send_text(self, openid: str, text: str) -> bool:
        """Send a plain text message to a WeChat user."""
        token = self._get_access_token()
        if not token:
            return False

        import urllib.request

        body = json_dumps({
            "touser": openid,
            "msgtype": "text",
            "text": {"content": text},
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}",
                data=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                errcode = data.get("errcode", -1)
                if errcode != 0:
                    logger.error("Weixin send failed: errcode=%s errmsg=%s",
                                 errcode, data.get("errmsg", ""))
                    return False
                return True
        except Exception as exc:
            logger.error("Weixin send exception: %s", exc)
            return False

    def send_news(self, openid: str, articles: list[dict[str, str]]) -> bool:
        """Send news (article) messages to a WeChat user.

        Each article dict: {"title": "...", "description": "...", "url": "...", "picurl": "..."}
        """
        token = self._get_access_token()
        if not token:
            return False

        import urllib.request

        body = json_dumps({
            "touser": openid,
            "msgtype": "news",
            "news": {"articles": articles},
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}",
                data=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                return data.get("errcode", -1) == 0
        except Exception as exc:
            logger.error("Weixin news send exception: %s", exc)
            return False

    # ── access token management ──

    def _get_access_token(self) -> str | None:
        """Get a valid access token, refreshing if expired (2h lifetime, 5min buffer)."""
        if self._access_token and time.time() < self._token_expire_time:
            return self._access_token

        import urllib.request

        url = (
            "https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        )
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                token = data.get("access_token", "")
                if not token:
                    logger.error("Failed to get Weixin access token: %s", data.get("errmsg", ""))
                    return None
                expires_in = data.get("expires_in", 7200)
                self._access_token = token
                self._token_expire_time = time.time() + expires_in - 300
                logger.info("Weixin access token refreshed, expires in %ds", expires_in)
                return token
        except Exception as exc:
            logger.error("Weixin access token exception: %s", exc)
            return None


