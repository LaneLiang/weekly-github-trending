"""Unified LLM API client supporting OpenAI and Anthropic backends."""

import re

from dc_auto_tune.utils.types_ import MetaOptConfig


class LLMClient:
    """Thin wrapper around OpenAI / Anthropic chat-completion APIs.

    Instantiates the correct SDK client based on ``MetaOptConfig.llm_provider``
    and exposes a single ``chat(system_prompt, user_prompt) -> str`` method.
    """

    def __init__(self, config: MetaOptConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key
        self._client: object | None = None

    @property
    def client(self):
        """Lazy-initialized SDK client."""
        if self._client is None:
            self._setup_client()
        return self._client

    def _setup_client(self) -> None:
        if self.config.llm_provider == "openai":
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        elif self.config.llm_provider == "anthropic":
            from anthropic import Anthropic

            self._client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(
                f"Unknown LLM provider: {self.config.llm_provider}"
            )

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat completion request and return the text content."""
        if self.config.llm_provider == "openai":
            resp = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.temperature,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content
        elif self.config.llm_provider == "anthropic":
            resp = self.client.messages.create(
                model=self.config.llm_model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=self.config.temperature,
            )
            content = resp.content[0].text
            return self._extract_json(content)
        else:
            raise ValueError(
                f"Unknown LLM provider: {self.config.llm_provider}"
            )

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract the first JSON object from a string (for Anthropic responses)."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group(0) if match else "{}"
