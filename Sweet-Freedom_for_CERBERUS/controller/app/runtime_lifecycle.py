from __future__ import annotations

from enum import Enum
from time import time
from pydantic import BaseModel, Field


class LifecyclePhase(str, Enum):
    BOOTING = "booting"
    READY = "ready"
    ENGAGED = "engaged"
    DEGRADED = "degraded"
    FAULTED = "faulted"


class RuntimeLifecycleState(BaseModel):
    phase: LifecyclePhase = LifecyclePhase.BOOTING
    reason: str = "starting"
    updated_at: float = Field(default_factory=time)


class RuntimeLifecycleManager:
    def __init__(self) -> None:
        self.state = RuntimeLifecycleState()

    def set_ready(self, reason: str = "runtime ready") -> RuntimeLifecycleState:
        self.state.phase = LifecyclePhase.READY
        self.state.reason = reason
        self.state.updated_at = time()
        return self.state

    def set_engaged(self, reason: str = "command activity") -> RuntimeLifecycleState:
        self.state.phase = LifecyclePhase.ENGAGED
        self.state.reason = reason
        self.state.updated_at = time()
        return self.state

    def set_degraded(self, reason: str = "degraded") -> RuntimeLifecycleState:
        self.state.phase = LifecyclePhase.DEGRADED
        self.state.reason = reason
        self.state.updated_at = time()
        return self.state

    def set_faulted(self, reason: str = "faulted") -> RuntimeLifecycleState:
        self.state.phase = LifecyclePhase.FAULTED
        self.state.reason = reason
        self.state.updated_at = time()
        return self.state

    def recover(self) -> RuntimeLifecycleState:
        self.state.phase = LifecyclePhase.READY
        self.state.reason = "manual recovery"
        self.state.updated_at = time()
        return self.state

    def snapshot(self) -> dict:
        return self.state.model_dump(mode="json")
