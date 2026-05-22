import email
import imaplib
import logging
from datetime import date, datetime, timedelta
from email.header import decode_header
from typing import Any

from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import llm_chat

logger = logging.getLogger("lanes_ceo.mail")

PAPER_KEYWORDS = [
    "accept", "reject", "decision", "review", "revision",
    "minor revision", "major revision", "manuscript", "submission", "editor",
]

MAIL_DIGEST_SYSTEM = (
    "你是一名行政秘书，需要为博士生整理今日邮件摘要。"
    "对每封邮件用1行概括发件人、主题、关键内容。"
    "如果有论文相关邮件（录用/拒稿/修改/审稿），用【重要】标注并说明原因。"
    "总计300字以内。"
)


class MailDigestWorkflow:
    role_group = "mail_digest"
    actor_name = "mail-digest-actor"
    critic_name = "mail-digest-critic"

    def run_actor(self, job: Job) -> Artifact:
        message = job.input.get("message", "today")

        emails = _fetch_recent_emails()
        if emails:
            email_text = _format_email_list(emails)
            summary = llm_chat(MAIL_DIGEST_SYSTEM, f"今日邮件列表：\n{email_text}") or email_text
            paper_flags = [
                f"论文相关邮件: {e['subject']} (来自 {e['from']})"
                for e in emails if should_keep_unread(e["subject"])
            ]
            sources = ["mail-inbox-imap"]
        else:
            summary = (
                f"邮件摘要（{_today()}）：\n"
                f"（IMAP 未配置，请设置 LANES_CEO_EMAIL_* 环境变量）\n"
                f"触发消息: {message}"
            )
            paper_flags = []
            sources = ["unavailable"]

        risks = ["sensitive email content exposure"] if emails else ["email unavailable"]

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="mail_digest",
            summary=summary,
            artifact_paths=[],
            sources=sources,
            risks=risks + (["paper decision emails require unread preservation"] if paper_flags else []),
            user_confirmations=paper_flags + ["是否有需要额外关注的紧急邮件"],
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues = _check_digest_quality(artifact)
        approved = len(issues) == 0
        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=85 - len(issues) * 12,
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="邮件摘要审核通过" if approved else "请重新检查邮件摘要",
        )

    @staticmethod
    def should_keep_unread(subject: str) -> bool:
        return should_keep_unread(subject)


def should_keep_unread(subject: str) -> bool:
    return any(kw.lower() in subject.lower() for kw in PAPER_KEYWORDS)


def _fetch_recent_emails(hours: int = 48) -> list[dict[str, str]] | None:
    try:
        from lanes_ceo.config import Config

        cfg = Config.from_env()
        if not cfg.email_enabled or not cfg.email_address or not cfg.email_password:
            return None

        server = _connect_imap(cfg)
        if not server:
            return None

        try:
            return _search_recent(server, hours)
        finally:
            try:
                server.logout()
            except Exception:
                pass
    except Exception as exc:
        logger.warning("Mail fetch failed: %s", exc)
        return None


def _connect_imap(cfg: Any):
    server_addr = cfg.email_imap_server or "imap.gmail.com"
    try:
        if server_addr == "imap.gmail.com":
            server = imaplib.IMAP4_SSL(server_addr, 993)
        else:
            server = imaplib.IMAP4_SSL(server_addr)
        server.login(cfg.email_address, cfg.email_password)
        return server
    except Exception as exc:
        logger.warning("IMAP connect/login failed: %s", exc)
        return None


def _search_recent(server: imaplib.IMAP4, hours: int) -> list[dict[str, str]]:
    server.select("INBOX")
    since = (datetime.now() - timedelta(hours=hours)).strftime("%d-%b-%Y")
    status, data = server.search(None, f"(SINCE {since})")
    if status != "OK":
        return []

    email_ids = data[0].split()
    emails: list[dict[str, str]] = []
    for eid in reversed(email_ids[-20:]):
        status, msg_data = server.fetch(eid, "(RFC822)")
        if status != "OK":
            continue
        try:
            msg = email.message_from_bytes(msg_data[0][1])
            subject = _decode_header(msg["Subject"] or "(no subject)")
            from_addr = _decode_header(msg["From"] or "(unknown)")
            emails.append({"subject": subject, "from": from_addr, "id": eid.decode()})
        except Exception:
            continue
    return emails


def _decode_header(raw: str) -> str:
    parts = decode_header(raw)
    result = ""
    for text, charset in parts:
        if isinstance(text, bytes):
            result += text.decode(charset or "utf-8", errors="replace")
        else:
            result += text
    return result


def _format_email_list(emails: list[dict[str, str]]) -> str:
    lines = []
    for e in emails:
        flag = " [论文]" if should_keep_unread(e["subject"]) else ""
        lines.append(f"- {e['from']}: {e['subject']}{flag}")
    return "\n".join(lines)


def _today() -> str:
    return date.today().isoformat()


def _check_digest_quality(artifact: Artifact) -> list[str]:
    issues = []
    if len(artifact.summary) < 60:
        issues.append("邮件摘要内容过短（<60字）")
    if "mail-inbox" not in str(artifact.sources) and "unavailable" not in str(artifact.sources):
        issues.append("邮件来源未经验证")
    return issues
