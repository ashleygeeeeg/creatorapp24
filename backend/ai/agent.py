"""Safe YuCode-style planning primitives for CreatorApp24."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .providers import AIProviderError, ChatTurn, create_provider


@dataclass(frozen=True)
class AgentStep:
    id: str
    title: str
    description: str
    action: str = "edit"
    status: str = "pending"


@dataclass(frozen=True)
class AgentPlan:
    id: str
    prompt: str
    steps: list[AgentStep]


def _fallback_plan(prompt: str) -> AgentPlan:
    return AgentPlan(
        id=str(uuid.uuid4()),
        prompt=prompt,
        steps=[
            AgentStep(str(uuid.uuid4()), "Inspect project", "Review the relevant files and project structure.", "inspect"),
            AgentStep(str(uuid.uuid4()), "Plan changes", "Identify the smallest set of changes required.", "plan"),
            AgentStep(str(uuid.uuid4()), "Implement", "Apply the requested changes as pending edits for review.", "edit"),
            AgentStep(str(uuid.uuid4()), "Verify", "Run the appropriate checks in an isolated runner.", "verify"),
        ],
    )


def _parse_steps(raw: str) -> list[AgentStep]:
    try:
        payload: Any = json.loads(raw)
        items = payload.get("steps", []) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            return []
        result: list[AgentStep] = []
        for item in items[:12]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if title and description:
                result.append(
                    AgentStep(
                        id=str(uuid.uuid4()),
                        title=title,
                        description=description,
                        action=str(item.get("action", "edit")),
                    )
                )
        return result
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


async def create_plan(prompt: str, context: Sequence[ChatTurn] = ()) -> AgentPlan:
    """Generate a reviewable plan. This function never executes tools or shell commands."""
    clean_prompt = prompt.strip()
    if not clean_prompt:
        raise ValueError("prompt must not be empty")

    provider = create_provider(os.getenv("AI_PROVIDER"))
    messages = [
        ChatTurn(
            role="system",
            content=(
                "You are a coding-agent planner. Return JSON only with a top-level "
                "'steps' array. Each step must contain title, description, and action. "
                "Allowed actions: inspect, plan, edit, verify. Never propose executing "
                "arbitrary shell commands. Keep the plan concrete and reviewable."
            ),
        ),
        *context,
        ChatTurn(role="user", content=clean_prompt),
    ]
    try:
        raw = await provider.generate(messages)
        steps = _parse_steps(raw)
    except (AIProviderError, Exception):
        steps = []

    if not steps:
        return _fallback_plan(clean_prompt)
    return AgentPlan(id=str(uuid.uuid4()), prompt=clean_prompt, steps=steps)


def plan_to_dict(plan: AgentPlan) -> dict[str, Any]:
    return {"id": plan.id, "prompt": plan.prompt, "steps": [asdict(step) for step in plan.steps]}
