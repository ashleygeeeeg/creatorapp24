"""Provider-neutral text generation for CreatorApp24.

The application talks to this small interface rather than coupling itself to a
specific AI vendor. OpenAI is the default hosted provider; a llama.cpp/OpenAI-
compatible HTTP endpoint can be selected for local models.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from openai import AsyncOpenAI


class AIProviderError(RuntimeError):
    """Raised when an AI provider cannot produce a response."""


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class AIProvider(Protocol):
    async def generate(
        self,
        messages: Sequence[ChatTurn],
        *,
        model: str | None = None,
    ) -> str:
        ...


class OpenAIProvider:
    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        if not api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured")
        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = AsyncOpenAI(**kwargs)
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def generate(
        self,
        messages: Sequence[ChatTurn],
        *,
        model: str | None = None,
    ) -> str:
        try:
            result = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": turn.role, "content": turn.content}
                    for turn in messages
                ],
            )
        except Exception as exc:
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

        content = result.choices[0].message.content if result.choices else None
        if not content:
            raise AIProviderError("AI provider returned an empty response")
        return content


def create_provider(provider: str | None = None) -> AIProvider:
    """Create the configured provider without exposing provider credentials."""
    selected = (provider or os.getenv("AI_PROVIDER", "openai")).lower()
    if selected in {"openai", "openai-compatible", "local"}:
        return OpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("AI_BASE_URL") or None,
        )
    raise AIProviderError(f"Unsupported AI provider: {selected}")
