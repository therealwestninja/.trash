from __future__ import annotations

from enum import Enum
from time import time
from uuid import uuid4

from pydantic import BaseModel, Field


class GoalStatus(str, Enum):
    CREATED = "created"
    ACCEPTED = "accepted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    BLOCKED = "blocked"


class ActionGoal(BaseModel):
    goal_id: str = Field(default_factory=lambda: f"goal_{uuid4().hex[:10]}")
    action_type: str
    params: dict = Field(default_factory=dict)
    requested_by: str = "ui"
    priority: int = 50
    created_at: float = Field(default_factory=time)
    deadline: float | None = None


class ActionFeedback(BaseModel):
    goal_id: str
    status: GoalStatus
    progress: float = 0.0
    phase: str = "pending"
    message: str = ""


class ActionResult(BaseModel):
    goal_id: str
    status: GoalStatus
    success: bool
    code: str = "ok"
    message: str = ""
    details: dict = Field(default_factory=dict)


class CancelRequest(BaseModel):
    goal_id: str
    requested_by: str = "ui"
