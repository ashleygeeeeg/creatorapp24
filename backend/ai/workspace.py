"""Mongo-backed workspace state for the CreatorApp24 coding workspace."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid


async def create_workspace(db, user_id: str, name: str, build_id: str | None = None) -> dict[str, Any]:
    workspace = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "build_id": build_id,
        "name": name.strip() or "Untitled workspace",
        "files": {},
        "pending_changes": [],
        "verification": {"status": "not_run", "message": None},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.workspaces.insert_one(workspace)
    return {k: v for k, v in workspace.items() if k != "_id"}


async def get_workspace(db, workspace_id: str, user_id: str) -> dict[str, Any] | None:
    return await db.workspaces.find_one({"id": workspace_id, "user_id": user_id}, {"_id": 0})
