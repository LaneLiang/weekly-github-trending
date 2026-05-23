"""Feishu message sender — sends notifications back to Feishu chat groups.

Uses the Feishu Open API to:
  - Send text messages to group chats
  - Send rich card messages for job completion notifications
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("lanes_ceo.feishu_sender")


@dataclass
class FeishuConfig:
    app_id: str
    app_secret: str


class FeishuSender:
    """Sends messages to Feishu via the Open API.

    Requires lark-oapi SDK to be installed.
    Can also work with just requests (fallback HTTP mode).
    """

    def __init__(self, config: FeishuConfig) -> None:
        self.app_id = config.app_id
        self.app_secret = config.app_secret
        self._client = None
        self._tenant_access_token: str | None = None
        self._token_expire_time: float = 0

    def _get_client(self):
        """Lazy-init the Lark API client or fall back to HTTP."""
        if self._client is not None:
            return self._client

        # Prefer HTTP fallback for reliability — avoids SDK version mismatches
        try:
            import lark_oapi as lark
            client = lark.Client.builder() \
                .app_id(self.app_id) \
                .app_secret(self.app_secret) \
                .build()
            # Test that the required classes exist
            _ = lark.api.im.v1.CreateMessageReqBody
            self._client = client
            logger.info("Feishu client initialized via lark-oapi SDK")
            return client
        except (ImportError, AttributeError):
            logger.info("lark-oapi SDK unavailable or incompatible; using HTTP fallback")
            self._client = "http-fallback"
            return self._client

    def send_text(self, chat_id: str, text: str) -> bool:
        """Send a plain text message to a Feishu chat/group."""
        client = self._get_client()

        if client == "http-fallback":
            return self._send_text_http(chat_id, text)

        try:
            import lark_oapi as lark

            body = lark.api.im.v1.CreateMessageReqBody(
                receive_id=chat_id,
                msg_type="text",
                content=json_dumps({"text": text}),
            )
            req = lark.im.v1.create_message.CreateMessageReq.builder() \
                .receive_id_type("chat_id") \
                .request_body(body) \
                .build()
            resp = client.im.v1.message.create(req)
            if not resp.success():
                logger.error("Feishu send failed: code=%s msg=%s",
                             resp.code, resp.msg)
                return False
            return True
        except Exception as exc:
            logger.error("Feishu send exception: %s", exc)
            return False

    def send_card(self, chat_id: str, title: str, content: str) -> bool:
        """Send a rich card message to a Feishu chat."""
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content,
                }
            ],
        }

        client = self._get_client()
        if client == "http-fallback":
            return self._send_card_http(chat_id, card)

        try:
            import lark_oapi as lark

            body = lark.api.im.v1.CreateMessageReqBody(
                receive_id=chat_id,
                msg_type="interactive",
                content=json_dumps(card),
            )
            req = lark.im.v1.create_message.CreateMessageReq.builder() \
                .receive_id_type("chat_id") \
                .request_body(body) \
                .build()
            resp = client.im.v1.message.create(req)
            return resp.success()
        except Exception as exc:
            logger.error("Feishu card send exception: %s", exc)
            return False

    # ── HTTP fallback (no lark-oapi SDK needed) ──

    def _get_tenant_token_http(self) -> str | None:
        import time
        import urllib.request

        if self._tenant_access_token and time.time() < self._token_expire_time:
            return self._tenant_access_token

        try:
            body = json_dumps({
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                data=body,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                self._tenant_access_token = data.get("tenant_access_token", "")
                expire = data.get("expire", 7200)
                self._token_expire_time = time.time() + expire - 300
                return self._tenant_access_token
        except Exception as exc:
            logger.error("Failed to get tenant access token: %s", exc)
            return None

    def _send_text_http(self, chat_id: str, text: str) -> bool:
        import urllib.request

        token = self._get_tenant_token_http()
        if not token:
            return False

        try:
            body = json_dumps({
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json_dumps({"text": text}),
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                code = data.get("code", -1)
                if code != 0:
                    logger.error("Feishu HTTP send failed: %s", data.get("msg", ""))
                    return False
                return True
        except Exception as exc:
            logger.error("Feishu HTTP send exception: %s", exc)
            return False

    def _send_card_http(self, chat_id: str, card: dict) -> bool:
        import urllib.request

        token = self._get_tenant_token_http()
        if not token:
            return False

        try:
            body = json_dumps({
                "receive_id": chat_id,
                "msg_type": "interactive",
                "content": json_dumps(card),
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json_loads(resp.read())
                return data.get("code", -1) == 0
        except Exception as exc:
            logger.error("Feishu card HTTP send exception: %s", exc)
            return False


def json_dumps(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


def json_loads(data: bytes) -> dict:
    import json
    return json.loads(data)
