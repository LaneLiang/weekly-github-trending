"""Shared utilities for workflow implementations."""

import logging
import os
from pathlib import Path

logger = logging.getLogger("lanes_ceo.utils")

HUMANIZER_SUFFIX = (
    "【写作风格要求】请使用自然流畅的中文表达，避免以下AI生成常见问题：\n"
    "1. 不要使用「在当今时代」「随着…的发展」「综上所述」等模板句式；\n"
    "2. 句子长短交替，避免连续使用相同句式；\n"
    "3. 使用具体数据、实例而非抽象空泛的表述；\n"
    "4. 语气真诚、直接，像一位严谨的研究者在做书面汇报；\n"
    "5. 避免堆砌形容词和副词，用动词和名词驱动句子。"
)


def llm_chat(system_prompt: str, user_prompt: str) -> str | None:
    """Call LLM with humanizer instructions appended. Returns None on failure."""
    full_system = f"{system_prompt}\n\n{HUMANIZER_SUFFIX}"
    try:
        from lanes_ceo.config import Config
        from lanes_ceo.llm import LLMClient

        cfg = Config.from_env()
        llm = LLMClient(cfg)
        response = llm.chat(full_system, user_prompt)
        if response.startswith("[LLM"):
            logger.warning("LLM returned fallback placeholder — check API key and model config")
            return None
        return response
    except Exception as exc:
        logger.error("LLM call failed: %s (%s)", exc, type(exc).__name__)
        return None


PROJECT_OUTPUT_BASE = Path(
    os.getenv(
        "LANES_CEO_OUTPUT_BASE",
        "G:/blog/claude_code_useage/PROJECT/multi-agent",
    )
)

_ARTIFACT_TYPE_DIR_MAP: dict[str, str] = {
    "weekly_report": "weekly_reports",
    "presentation": "presentations",
    "daily_report": "daily_reports",
    "reflection": "reflections",
    "paper_draft": "paper_drafts",
    "paper_research": "paper_research",
    "mail_digest": "mail_digests",
    "github_trending": "briefings",
    "ai_news": "briefings",
    "update_check": "update_checks",
    "memory_curation": "memory_curation",
    "literature_survey": "literature_survey",
    "fake": "debug",
    "eda_testbench": "eda_testbench",
    "deepseek_monitor": "deepseek_monitor",
}


def get_artifact_dir(artifact_type: str) -> Path:
    """Return the categorized output directory for a given artifact type, creating it if needed."""
    subdir = _ARTIFACT_TYPE_DIR_MAP.get(artifact_type, artifact_type)
    target = PROJECT_OUTPUT_BASE / subdir
    target.mkdir(parents=True, exist_ok=True)
    return target
