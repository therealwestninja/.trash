from __future__ import annotations

from pydantic import BaseModel, Field


class OperatorTextRequest(BaseModel):
    text: str = ""


class QuickActionRequest(BaseModel):
    action: str


class GoalCancelRequest(BaseModel):
    goal_id: str
    requested_by: str = "ui"


class ControlSourceRequest(BaseModel):
    source: str


class SessionAcquireRequest(BaseModel):
    owner: str = "ui"


class SessionCheckinRequest(BaseModel):
    lease_id: str


class SessionReleaseRequest(BaseModel):
    lease_id: str


class ReplayLoadRequest(BaseModel):
    jsonl: str


class SimpleActionResponse(BaseModel):
    ok: bool = True
    message: str = ""


class PresenceTickResponse(BaseModel):
    idle_behavior: str | None = None
    idle_counter: int | None = None


class HealthResponse(BaseModel):
    status: str


class EventEnvelope(BaseModel):
    type: str
    data: dict = Field(default_factory=dict)


class SessionSummaryResponse(BaseModel):
    active: bool
    lease: dict | None = None
    policy: dict | None = None
    degraded: bool = False


class DiagnosticsResponse(BaseModel):
    timestamp: float | None = None
    summary: dict = Field(default_factory=dict)
    safety: dict = Field(default_factory=dict)
    session: dict = Field(default_factory=dict)
    telemetry: dict = Field(default_factory=dict)
    goal: dict = Field(default_factory=dict)
    goal_result: dict = Field(default_factory=dict)
    command_mux: dict = Field(default_factory=dict)


class ReplayStateResponse(BaseModel):
    is_loaded: bool
    cursor: int
    event_count: int
    next_event: dict | None = None
    started_at: float | None = None


class CapabilityRegistryResponse(BaseModel):
    count: int
    categories: list[str] = Field(default_factory=list)
    capabilities: list[dict] = Field(default_factory=list)
