from lanes_ceo.contracts import TaskRequest
from lanes_ceo.enums import SourceChannel


class HermesFeishuAdapter:
    source_channel = SourceChannel.FEISHU.value

    def receive(self, raw_event: dict) -> TaskRequest:
        return TaskRequest(
            request_id=raw_event.get("event_id", f"feishu-{raw_event.get('message_id', 'unknown')}"),
            source_channel=SourceChannel.FEISHU,
            sender=raw_event.get("sender_id", "unknown"),
            raw_message=raw_event.get("text", ""),
            task_intent=raw_event.get("intent", "unknown"),
            priority="normal",
            attachments=raw_event.get("attachments", []),
            authorization_context={
                "platform": "feishu",
                "chat_id": raw_event.get("chat_id"),
            },
        )


class HermesWeixinAdapter:
    source_channel = SourceChannel.WEIXIN.value

    def receive(self, raw_event: dict) -> TaskRequest:
        return TaskRequest(
            request_id=raw_event.get("event_id", f"weixin-{raw_event.get('message_id', 'unknown')}"),
            source_channel=SourceChannel.WEIXIN,
            sender=raw_event.get("sender_id", "unknown"),
            raw_message=raw_event.get("text", ""),
            task_intent=raw_event.get("intent", "unknown"),
            priority="normal",
            authorization_context={
                "platform": "weixin",
                "chat_id": raw_event.get("chat_id"),
            },
        )


class HermesQQBotAdapter:
    source_channel = SourceChannel.QQ.value

    def receive(self, raw_event: dict) -> TaskRequest:
        return TaskRequest(
            request_id=raw_event.get("event_id", f"qq-{raw_event.get('message_id', 'unknown')}"),
            source_channel=SourceChannel.QQ,
            sender=raw_event.get("sender_id", "unknown"),
            raw_message=raw_event.get("text", ""),
            task_intent=raw_event.get("intent", "unknown"),
            priority="normal",
            authorization_context={
                "platform": "qq",
                "chat_id": raw_event.get("chat_id"),
            },
        )
