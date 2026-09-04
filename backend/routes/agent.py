"""YuCode-style coding workspace API routes."""

from __future__ import annotations

from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ai.agent import create_plan, plan_to_dict
from ai.providers import ChatTurn
from ai.workspace import create_workspace, get_workspace


class WorkspaceCreate(BaseModel):
    name: str = Field(default="Untitled workspace", max_length=120)
    build_id: Optional[str] = None


class PlanRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    session_id: Optional[str] = None
    workspace_id: Optional[str] = None


class PendingChangeCreate(BaseModel):
    workspace_id: str
    path: str = Field(min_length=1, max_length=500)
    before: str = ""
    after: str
    description: str = Field(default="AI-generated change", max_length=1000)


async def _current_user():
    # Import at request time to avoid a circular import during server startup.
    from server import get_current_user
    return await get_current_user()


def _db():
    # Import at request time so this route module remains independently testable.
    from server import db
    return db


def register(router: APIRouter) -> None:
    @router.post("/agent/workspaces")
    async def create_agent_workspace(data: WorkspaceCreate, user=Depends(_current_user)):
        if data.build_id:
            build = await _db().builds.find_one({"id": data.build_id, "user_id": user["id"]}, {"_id": 0})
            if not build:
                raise HTTPException(status_code=404, detail="Build not found")
        return await create_workspace(_db(), user["id"], data.name, data.build_id)

    @router.get("/agent/workspaces/{workspace_id}")
    async def read_agent_workspace(workspace_id: str, user=Depends(_current_user)):
        workspace = await get_workspace(_db(), workspace_id, user["id"])
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace

    @router.post("/agent/plan")
    async def create_agent_plan(data: PlanRequest, user=Depends(_current_user)):
        workspace = None
        if data.workspace_id:
            workspace = await get_workspace(_db(), data.workspace_id, user["id"])
            if not workspace:
                raise HTTPException(status_code=404, detail="Workspace not found")

        build_count = await _db().builds.count_documents(
            {"user_id": user["id"], "payment_status": {"$in": ["free", "paid", "mock_paid"]}}
        )
        if build_count == 0:
            raise HTTPException(status_code=403, detail="Create or pay for a build before generating implementation plans")

        session_id = data.session_id or str(uuid.uuid4())
        history = await _db().chat_history.find(
            {"session_id": session_id, "user_id": user["id"]}, {"_id": 0}
        ).sort("created_at", 1).to_list(20)
        context = [
            ChatTurn(role=item["role"], content=item["content"])
            for item in history
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ]
        plan = await create_plan(data.prompt, context)
        doc: dict[str, Any] = {
            "id": plan.id,
            "session_id": session_id,
            "user_id": user["id"],
            "workspace_id": data.workspace_id,
            "prompt": data.prompt,
            "plan": plan_to_dict(plan),
        }
        await _db().agent_plans.insert_one(doc)
        return {"session_id": session_id, "workspace_id": data.workspace_id, "plan": plan_to_dict(plan)}

    @router.post("/agent/changes")
    async def create_pending_change(data: PendingChangeCreate, user=Depends(_current_user)):
        workspace = await get_workspace(_db(), data.workspace_id, user["id"])
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        change = {
            "id": str(uuid.uuid4()),
            "workspace_id": data.workspace_id,
            "user_id": user["id"],
            "path": data.path,
            "before": data.before,
            "after": data.after,
            "description": data.description,
            "status": "pending",
        }
        await _db().agent_changes.insert_one(change)
        return {k: v for k, v in change.items() if k != "_id"}

    @router.get("/agent/sessions/{session_id}")
    async def get_agent_session(session_id: str, user=Depends(_current_user)):
        plans = await _db().agent_plans.find(
            {"session_id": session_id, "user_id": user["id"]}, {"_id": 0}
        ).sort("_id", 1).to_list(50)
        return {"session_id": session_id, "plans": plans}
