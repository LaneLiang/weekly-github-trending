"""Shared ingress utilities — intent recognition, response building, message helpers.

Used by FeishuBridge, WeixinBridge, and QQBotBridge to avoid duplicating
intent classification and response formatting logic.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("lanes_ceo.ingress.shared")

# ── role / intent mapping ──

ROLE_LABELS: dict[str, str] = {
    "weekly_report": "周报",
    "presentation": "PPT汇报",
    "daily_report": "日报",
    "reflection": "反思",
    "paper_writing": "论文草稿",
    "paper_research": "文献调研",
    "mail_digest": "邮件摘要",
    "github_trending": "GitHub热点",
    "ai_news": "AI新闻简报",
    "claude_task": "任务执行",
    "fake": "测试",
}

FILE_PRODUCING_ROLES = {"weekly_report", "presentation"}


def infer_intent(text: str) -> str | None:
    """Naive intent classifier based on keywords. Returns None for unknown intents."""
    kw_map = {
        "周报": "weekly_report",
        "日报": "daily_report",
        "总结": "daily_report",
        "PPT": "presentation",
        "汇报": "presentation",
        "论文": "paper_writing",
        "文献": "paper_research",
        "邮件": "mail_digest",
        "反思": "reflection",
        "GitHub": "github_trending",
        "AI新闻": "ai_news",
        "新闻": "ai_news",
    }
    for kw, intent in kw_map.items():
        if kw in text:
            return intent
    return None


def infer_role_group(text: str) -> str | None:
    """Map natural language trigger words to role_group. Returns None for unknowns."""
    kw_map = {
        "周报": "weekly_report",
        "周总结": "weekly_report",
        "PPT": "presentation",
        "汇报": "presentation",
        "日报": "daily_report",
        "总结": "daily_report",
        "反思": "reflection",
        "论文": "paper_writing",
        "写论文": "paper_writing",
        "文献": "paper_research",
        "调研": "paper_research",
        "邮件": "mail_digest",
        "收件箱": "mail_digest",
        "GitHub": "github_trending",
        "hot": "github_trending",
        "新闻": "ai_news",
        "AI新闻": "ai_news",
        "测试": "claude_task",
        "跑测试": "claude_task",
        "提交": "claude_task",
        "最近提交": "claude_task",
        "状态": "claude_task",
        "项目状态": "claude_task",
        "历史": "claude_task",
        "记录": "claude_task",
    }
    for kw, role in kw_map.items():
        if kw in text:
            return role
    return None


def is_history_query(text: str) -> bool:
    """Check if the message is asking for task execution history."""
    history_words = ["历史", "记录", "上次", "最近执行"]
    return any(w in text for w in history_words)


def check_permission(sender_id: str) -> bool:
    """Check if sender_id is in the allowed_users whitelist. Empty list = allow all."""
    from lanes_ceo.workflows.claude_task import get_allowed_users

    allowed = get_allowed_users()
    if not allowed:
        return True
    return sender_id in allowed


# ── response building ──

def status_label(status_value: str) -> str:
    labels = {
        "received": "已接收",
        "running_actor": "生成中…",
        "waiting_review": "审核中…",
        "approved": "已完成",
        "notified": "已完成",
        "returned_to_actor": "已退回",
    }
    return labels.get(status_value, status_value)


def build_response(role_group: str, job, artifact) -> str:
    """Build a chat message containing the actual generated content."""
    label = ROLE_LABELS.get(role_group, role_group)
    st_label = status_label(job.status.value)

    if artifact is None:
        return f"【{label}】{st_label}\nJob ID: {job.job_id}\n(未生成内容)"

    if job.status.value == "returned_to_actor":
        return f"【{label}】审核未通过，已退回修改\nJob ID: {job.job_id}"

    header = f"【{label}】{st_label}\n"

    if role_group in FILE_PRODUCING_ROLES:
        file_info = ""
        if artifact.artifact_paths:
            file_info = f"文件: {artifact.artifact_paths[0]}\n"
        summary_excerpt = truncate(artifact.summary, 600)
        return f"{header}{file_info}{summary_excerpt}"

    body = truncate(artifact.summary, 4000)
    return f"{header}\n{body}"


def truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def split_long_message(text: str, max_len: int = 3500) -> list[str]:
    """Split a message into chunks that fit within the length limit."""
    if len(text) <= max_len:
        return [text]

    paragraphs = text.split("\n")
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 > max_len:
            if current:
                chunks.append(current)
            current = para
        else:
            current = f"{current}\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


# ── JSON parsing ──

def json_parse_text(content_str: str) -> str:
    import json
    try:
        return json.loads(content_str).get("text", "")
    except Exception:
        return content_str


def json_parse_post(content_str: str) -> str:
    import json
    try:
        data = json.loads(content_str)
        parts = []
        for block in data.get("content", []):
            for elem in block:
                if isinstance(elem, dict) and "text" in elem:
                    parts.append(elem["text"])
        return " ".join(parts)
    except Exception:
        return ""


# ── help / unknown intent ──

HELP_TEXT = """【Lanes CEO 可用指令】

学术写作：
• 「周报」— 生成本周科研周报 (.docx)
• 「PPT」/「汇报」— 生成组会汇报 PPT (.pptx)
• 「论文」/「写论文」— 撰写论文草稿
• 「文献」/「调研」— 文献调研

日常记录：
• 「日报」/「总结」— 生成今日工作总结
• 「反思」— 生成今日反思

信息获取：
• 「新闻」/「AI新闻」— 本周 AI 新闻简报
• 「GitHub」/「hot」— GitHub 热点项目
• 「邮件」/「收件箱」— 邮件摘要

代码任务（claude 自动执行）：
• 「测试」/「跑测试」— 运行 pytest 并分析
• 「提交」/「最近提交」— 查看 git 提交记录
• 「状态」/「项目状态」— 查看项目未提交变更

发送以上任一关键词即可触发对应功能。其他问题我会尝试直接回答。"""

HELP_FOOTER = "━━━━━━━━━━\n发送「周报」「PPT」「日报」「论文」「新闻」等关键词触发专项功能"

GENERAL_CHAT_SYSTEM = (
    "你是 Lanes CEO，一位严谨、真诚的博士研究生个人助理。"
    "你的背景是数字IC设计领域，熟悉芯片设计、电力电子、深度学习等科研方向。"
    "对于用户的问题，给出简洁、准确、有帮助的回答。"
    "如果问题超出你的知识范围，诚实说明，不要编造。"
    "回复控制在300字以内，使用自然的中文表达。"
)


def general_chat(user_text: str) -> str | None:
    """Try to answer a general question via LLM. Returns None if LLM unavailable."""
    from lanes_ceo.workflows.utils import llm_chat

    try:
        return llm_chat(GENERAL_CHAT_SYSTEM, user_text)
    except Exception:
        logger.warning("LLM chat failed, falling back to help text")
        return None


def handle_unknown_intent(chat_id: str, text: str, send_fn) -> None:
    """Handle messages that don't match any known workflow.

    Three-tier response:
    1. Try general LLM chat for a natural answer
    2. If LLM unavailable, fall back to help text
    3. Always append available commands as a footer
    """
    logger.info("Unknown intent: %s", text[:80])

    llm_answer = general_chat(text)
    if llm_answer:
        response = f"{llm_answer}\n\n{HELP_FOOTER}"
        send_fn(chat_id, truncate(response, 4000))
        return

    send_fn(chat_id, HELP_TEXT)


def handle_task_history(chat_id: str, send_fn) -> None:
    """Send recent claude_task execution history to the chat (used by all bridges)."""
    from lanes_ceo.workflows.claude_task import get_recent_results

    results = get_recent_results(5)
    if not results:
        send_fn(chat_id, "暂无任务执行记录。")
        return

    lines = ["【最近任务执行记录】", ""]
    for i, r in enumerate(results, 1):
        desc = r.get("description", "未知任务")
        summary = r.get("summary", "")
        preview = summary[:120].replace("\n", " ")
        lines.append(f"{i}. {desc}")
        lines.append(f"   {preview}...")
        lines.append("")
    send_fn(chat_id, "\n".join(lines))


def json_dumps(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


def json_loads(data: bytes) -> dict:
    import json
    return json.loads(data)
