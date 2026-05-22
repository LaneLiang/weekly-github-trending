from lanes_ceo.ingress.hermes import (
    HermesFeishuAdapter,
    HermesQQBotAdapter,
    HermesWeixinAdapter,
)


def test_feishu_adapter_maps_event_to_task_request() -> None:
    adapter = HermesFeishuAdapter()
    event = {
        "event_id": "evt-001",
        "message_id": "msg-123",
        "sender_id": "ou_abc",
        "text": "帮我总结今天的邮件",
        "intent": "mail_digest",
        "chat_id": "oc_xyz",
    }
    req = adapter.receive(event)

    assert req.request_id == "evt-001"
    assert req.source_channel.value == "feishu"
    assert req.sender == "ou_abc"
    assert req.raw_message == "帮我总结今天的邮件"
    assert req.task_intent == "mail_digest"
    assert req.authorization_context["platform"] == "feishu"
    assert req.authorization_context["chat_id"] == "oc_xyz"


def test_weixin_adapter_maps_event_to_task_request() -> None:
    adapter = HermesWeixinAdapter()
    event = {
        "message_id": "wx-456",
        "sender_id": "user_wx",
        "text": "本周GitHub热点",
        "intent": "briefings",
    }
    req = adapter.receive(event)

    assert req.source_channel.value == "weixin"
    assert req.sender == "user_wx"
    assert req.raw_message == "本周GitHub热点"
    assert req.authorization_context["platform"] == "weixin"


def test_qqbot_adapter_maps_event_to_task_request() -> None:
    adapter = HermesQQBotAdapter()
    event = {
        "message_id": "qq-789",
        "sender_id": "qq_user_1",
        "text": "今日反思",
        "intent": "daily_loop",
    }
    req = adapter.receive(event)

    assert req.source_channel.value == "qq"
    assert req.task_intent == "daily_loop"
    assert req.authorization_context["platform"] == "qq"


def test_adapters_generate_fallback_request_id() -> None:
    adapter = HermesFeishuAdapter()
    req = adapter.receive({"text": "hello", "sender_id": "u1"})
    assert req.request_id.startswith("feishu-")
