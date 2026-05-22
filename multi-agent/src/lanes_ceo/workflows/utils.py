"""Shared utilities for workflow implementations."""

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
            return None
        return response
    except Exception:
        return None
