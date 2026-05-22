"""Minimal LLM client wrapper — pluggable for any OpenAI-compatible API."""

from lanes_ceo.config import Config


class LLMClient:
    def __init__(self, config: Config) -> None:
        self._cfg = config

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        provider = self._cfg.llm_provider
        api_key = self._cfg.llm_api_key
        base_url = self._cfg.llm_base_url
        model = self._cfg.llm_model

        if not api_key:
            return (
                "[LLM not configured] Set LANES_CEO_LLM_API_KEY and "
                "LANES_CEO_LLM_MODEL to enable AI responses.\n"
                f"System: {system_prompt[:200]}\n"
                f"User: {user_prompt[:200]}"
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=base_url or None)
            response = client.chat.completions.create(
                model=model or "gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            return f"[LLM error: {exc}]"
