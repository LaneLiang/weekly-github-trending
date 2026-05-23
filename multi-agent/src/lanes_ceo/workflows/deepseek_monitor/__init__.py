"""DeepSeek balance monitor — daily check of API account balance.

Queries the DeepSeek API balance endpoint and alerts when the remaining
balance drops below the configured threshold.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import date
from pathlib import Path

from lanes_ceo.config import Config
from lanes_ceo.contracts import Artifact, CriticReview, Job
from lanes_ceo.workflows.utils import get_artifact_dir

logger = logging.getLogger("lanes_ceo.deepseek_monitor")

BALANCE_URL = "https://api.deepseek.com/user/balance"


def _fetch_balance(api_key: str) -> dict:
    """Fetch DeepSeek account balance via HTTP GET.

    Returns:
        dict with keys: balance (float|None), is_available (bool|None),
        raw (str), error (str|None).
    """
    try:
        req = urllib.request.Request(
            BALANCE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            balance = None
            is_available = None

            # DeepSeek balance response structure varies — try known keys
            if "balance" in data:
                balance = float(data["balance"])
            elif "data" in data and isinstance(data["data"], dict):
                balance = data["data"].get("balance")
                if balance is not None:
                    balance = float(balance)
            elif "total_balance" in data:
                balance = float(data["total_balance"])

            is_available = data.get("is_available", True)
            if isinstance(is_available, str):
                is_available = is_available.lower() in ("true", "1", "yes")

            return {"balance": balance, "is_available": is_available, "raw": raw[:500], "error": None}
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")[:300]
        except Exception as exc_inner:
            logger.debug("Failed to read HTTP error body: %s", exc_inner)
        return {"balance": None, "is_available": False, "raw": body, "error": f"HTTP {exc.code}: {body}"}
    except Exception as exc:
        return {"balance": None, "is_available": False, "raw": "", "error": str(exc)}


class DeepSeekMonitorWorkflow:
    role_group = "deepseek_monitor"
    actor_name = "deepseek-monitor-actor"
    critic_name = "deepseek-monitor-critic"

    def run_actor(self, job: Job) -> Artifact:
        today = date.today().isoformat()
        logger.info("DeepSeekMonitor actor starting, job=%s", job.job_id)

        cfg = Config.from_env()
        api_key = cfg.deepseek_api_key
        threshold = cfg.deepseek_balance_threshold

        if not api_key:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="deepseek_monitor",
                summary="DeepSeek API key 未配置，跳过余额检查。\n请在 .env 中设置 LANES_CEO_DEEPSEEK_API_KEY。",
                artifact_paths=[],
                sources=[],
                risks=[],
                user_confirmations=[],
            )

        result = _fetch_balance(api_key)

        if result["error"]:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="deepseek_monitor",
                summary=f"# DeepSeek 余额检查失败 — {today}\n\n错误: {result['error']}",
                artifact_paths=[],
                sources=["deepseek-api"],
                risks=["API balance check failed — verify API key and network"],
                user_confirmations=[],
            )

        balance = result["balance"]
        is_available = result["is_available"]

        if balance is None:
            return Artifact(
                artifact_id=f"artifact-{job.job_id}",
                job_id=job.job_id,
                artifact_type="deepseek_monitor",
                summary=f"# DeepSeek 余额查询 — {today}\n\n余额数据无法解析，原始响应:\n```\n{result['raw']}\n```",
                artifact_paths=[],
                sources=["deepseek-api"],
                risks=["Unable to parse balance from API response — API may have changed"],
                user_confirmations=[],
            )

        below_threshold = balance < threshold

        lines = [
            f"# DeepSeek 余额{'告警' if below_threshold else '报告'} — {today}",
            "",
            f"- **当前余额**: ¥{balance:.2f}",
            f"- **告警阈值**: ¥{threshold:.2f}",
            f"- **API 可用**: {'是' if is_available else '否'}",
            f"- **状态**: {'⚠ 低于阈值，请尽快充值' if below_threshold else '正常 ✓'}",
        ]

        if below_threshold:
            lines.extend([
                "",
                "> ⚠ DeepSeek API 余额不足，所有依赖 LLM 的 workflow 将不可用。",
                "> 请登录 https://platform.deepseek.com 充值。",
            ])

        summary = "\n".join(lines)

        risks: list[str] = []
        confirmations: list[str] = []
        if below_threshold:
            risks.append(f"DeepSeek 余额 ¥{balance:.2f} 低于阈值 ¥{threshold:.2f}")
            confirmations.append("请确认已为 DeepSeek 账户充值")

        # Save report
        out_dir = get_artifact_dir("deepseek_monitor")
        ts = date.today().strftime("%Y%m%d")
        report_path = out_dir / f"deepseek-balance-{ts}.md"
        report_path.write_text(summary, encoding="utf-8")

        return Artifact(
            artifact_id=f"artifact-{job.job_id}",
            job_id=job.job_id,
            artifact_type="deepseek_monitor",
            summary=summary,
            artifact_paths=[str(report_path)],
            sources=["deepseek-api"],
            risks=risks,
            user_confirmations=confirmations,
        )

    def run_critic(self, job: Job, artifact: Artifact) -> CriticReview:
        issues: list[str] = []

        summary = artifact.summary

        if "API key 未配置" in summary:
            # Not configured is fine, no-op
            pass
        elif "检查失败" in summary:
            issues.append("DeepSeek API 调用失败 — 检查网络或 API key")
        elif "无法解析" in summary:
            issues.append("API 响应格式无法解析 — 可能 API 已变更")
        elif "当前余额" in summary:
            # Valid balance report — verify threshold logic
            if "低于阈值" in summary and len(artifact.risks) == 0:
                issues.append("余额低于阈值但未设置风险标记")
            if "低于阈值" not in summary and len(artifact.risks) > 0:
                issues.append("余额正常但存在风险标记")
        else:
            issues.append("余额报告格式异常")

        if "当前余额" in summary and len(artifact.artifact_paths) == 0:
            issues.append("余额报告未保存到文件")

        score = 95 - len(issues) * 15
        approved = len(issues) == 0

        return CriticReview(
            review_id=f"review-{job.job_id}",
            job_id=job.job_id,
            review_result="approved" if approved else "returned",
            score=max(score, 0),
            issues=issues,
            approved=approved,
            return_to_actor=not approved,
            handoff_note="DeepSeek 余额监控审核通过" if approved else f"发现 {len(issues)} 个问题，请修正",
        )
