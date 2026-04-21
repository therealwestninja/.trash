from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class RuntimeMode(str, Enum):
    SIMULATION = "simulation"
    REAL = "real"


class ActionType(str, Enum):
    IDLE = "idle"
    GREET = "greet"
    STOP = "stop"
    MOVE = "move"
    LOOK = "look"
    FOLLOW = "follow"


class ActionStatus(str, Enum):
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class OperatorInput(BaseModel):
    text: str = ""
    source: str = "operator"


class ActionRequest(BaseModel):
    action: ActionType
    reason: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    action: ActionType
    status: ActionStatus
    reason: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)


class SafetyState(BaseModel):
    estop_active: bool = False
    restricted: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    hardware_mode: RuntimeMode = RuntimeMode.SIMULATION


class RuntimeState(BaseModel):
    mode: RuntimeMode = RuntimeMode.SIMULATION
    operator_input: OperatorInput = Field(default_factory=OperatorInput)
    emotion: dict[str, float] = Field(default_factory=dict)
    presence: dict[str, Any] = Field(default_factory=dict)
    expression: dict[str, Any] = Field(default_factory=dict)
    animation: dict[str, Any] = Field(default_factory=dict)
    current_action: ActionRequest = Field(
        default_factory=lambda: ActionRequest(action=ActionType.IDLE, reason="startup")
    )
    last_action_result: ActionResult = Field(
        default_factory=lambda: ActionResult(
            action=ActionType.IDLE,
            status=ActionStatus.COMPLETED,
            reason="startup",
        )
    )
    safety: SafetyState = Field(default_factory=SafetyState)
    notes: list[str] = Field(default_factory=list)
    timestamp: float = 0.0
