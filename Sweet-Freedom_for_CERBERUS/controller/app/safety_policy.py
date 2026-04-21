from __future__ import annotations

from time import time
from typing import Any

from pydantic import BaseModel, Field


MOVEMENT_ACTIONS = {"move", "move_forward", "follow", "explore", "look"}


class SafetyState(BaseModel):
    estop_active: bool = False
    armed: bool = False
    allowed: bool = True
    reason: str = ""
    blocked_reasons: list[str] = Field(default_factory=list)
    last_updated: float = Field(default_factory=time)


class SafetyDecisionResult(BaseModel):
    status: str = "blocked"
    reason: str = ""
    action: str = ""


class SafetyPolicy:
    def __init__(self, hardware_mode: str = "simulation") -> None:
        self.hardware_mode = hardware_mode
        self.state = SafetyState()

    def evaluate(self, requested_action: Any) -> tuple[bool, str]:
        action_name = (
            getattr(requested_action, "action", None)
            or getattr(requested_action, "action_type", None)
            or "idle"
        )

        self.state.allowed = True
        self.state.reason = ""
        self.state.blocked_reasons = []
        self.state.last_updated = time()

        if self.state.estop_active:
            self.state.allowed = False
            self.state.reason = "E-Stop is latched"
            self.state.blocked_reasons.append(self.state.reason)
            return False, self.state.reason

        if action_name in MOVEMENT_ACTIONS and not self.state.armed:
            self.state.allowed = False
            self.state.reason = "System is disarmed"
            self.state.blocked_reasons.append(self.state.reason)
            return False, self.state.reason

        return True, "allowed"

    def trigger_estop(self) -> SafetyState:
        self.state.estop_active = True
        self.state.allowed = False
        self.state.reason = "E-Stop is latched"
        self.state.blocked_reasons = [self.state.reason]
        self.state.last_updated = time()
        return self.state

    def clear_estop(self) -> SafetyState:
        self.state.estop_active = False
        self.state.allowed = True
        self.state.reason = ""
        self.state.blocked_reasons = []
        self.state.last_updated = time()
        return self.state

    def arm(self) -> SafetyState:
        self.state.armed = True
        self.state.allowed = not self.state.estop_active
        self.state.reason = "" if not self.state.estop_active else "E-Stop is latched"
        self.state.blocked_reasons = [] if not self.state.estop_active else [self.state.reason]
        self.state.last_updated = time()
        return self.state

    def disarm(self) -> SafetyState:
        self.state.armed = False
        self.state.allowed = not self.state.estop_active
        self.state.reason = "System is disarmed"
        self.state.blocked_reasons = [self.state.reason]
        self.state.last_updated = time()
        return self.state

    def snapshot(self) -> SafetyState:
        self.state.last_updated = time()
        return self.state

    def make_blocked_result(self, requested_action: Any, reason: str) -> SafetyDecisionResult:
        action_name = (
            getattr(requested_action, "action", None)
            or getattr(requested_action, "action_type", None)
            or "unknown"
        )
        return SafetyDecisionResult(status="blocked", reason=reason, action=action_name)
