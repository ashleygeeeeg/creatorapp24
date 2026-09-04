"""Backward-compatible facade backed by the CreatorApp24 AI provider layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai.providers import ChatTurn, create_provider


@dataclass(frozen=True)
class UserMessage:
    text: str


class LlmChat:
    """Small compatibility facade for the legacy server.py chat contract."""

    def __init__(self, api_key: str, session_id: str, system_message: str) -> None:
        self.session_id = session_id
        self.system_message = system_message
        self.messages: list[dict[str, str]] = []
        self._model: str | None = None

    def with_model(self, provider: str, model: str) -> "LlmChat":
        self._model = model
        return self

    async def send_message(self, message: UserMessage) -> str:
        turns = [ChatTurn(role="system", content=self.system_message)]
        turns.extend(
            ChatTurn(role=item["role"], content=item["content"])
            for item in self.messages
            if item.get("role") in {"user", "assistant"} and item.get("content")
        )
        turns.append(ChatTurn(role="user", content=message.text))
        response = await create_provider().generate(turns, model=self._model)
        self.messages.append({"role": "user", "content": message.text})
        self.messages.append({"role": "assistant", "content": response})
        return response
