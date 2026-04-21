from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


COMMAND_CATEGORIES = ["motion", "behavior", "mission", "plugin", "body", "script", "arm", "bt", "always"]


class HardwareMode(str, Enum):
    REAL = "real"
    SIMULATION = "simulation"


class CommandStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class CommandState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EnvelopeType(str, Enum):
    TELEMETRY = "telemetry"
    COMMAND_UPDATE = "command_update"
    SYSTEM_STATE = "system_state"
    FAULT = "fault"
    WARNING = "warning"
    HEARTBEAT = "heartbeat"
    SNAPSHOT = "snapshot"


class HardwareState(BaseModel):
    mode: HardwareMode = HardwareMode.SIMULATION


class RobotState(BaseModel):
    platform: str = "unitree_go2"


class BridgeState(BaseModel):
    connected: bool = False


class SessionState(BaseModel):
    active: bool = False
    operator_id: str | None = None
    active_connections: int = 0


class CommandPolicy(BaseModel):
    allowed_categories: list[str] = Field(default_factory=lambda: ["always"])
    restricted: bool = True


class SimulationState(BaseModel):
    active: bool = True


class PluginFeatureState(BaseModel):
    enabled: bool = False
    features: list[str] = Field(default_factory=list)
    health: str = "unknown"


class FaultMessage(BaseModel):
    type: Literal["fault"] = "fault"
    severity: Literal["critical", "warning"]
    code: str
    message: str
    timestamp: float


class TelemetryPayload(BaseModel):
    battery_level: float = 100.0
    motion_state: str = "idle"
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0})
    docking_state: str = "undocked"
    safety_flags: list[str] = Field(default_factory=list)


class CommandRuntime(BaseModel):
    queue_depth: int = 0
    active_command_id: str | None = None
    total_commands_seen: int = 0
    last_command_id: str | None = None
    worker_started: bool = False


class SystemStatePayload(BaseModel):
    api_version: str = "1.2.0"
    hardware: HardwareState = Field(default_factory=HardwareState)
    robot: RobotState = Field(default_factory=RobotState)
    bridge: BridgeState = Field(default_factory=BridgeState)
    session: SessionState = Field(default_factory=SessionState)
    command_policy: CommandPolicy = Field(default_factory=CommandPolicy)
    simulation: SimulationState = Field(default_factory=SimulationState)
    telemetry: TelemetryPayload = Field(default_factory=TelemetryPayload)
    plugins: dict[str, PluginFeatureState] = Field(default_factory=dict)
    command_runtime: CommandRuntime = Field(default_factory=CommandRuntime)
    timestamp: float = 0.0


class EventEnvelope(BaseModel):
    type: EnvelopeType | str
    timestamp: float
    payload: dict[str, Any]


class ExecuteCommandRequest(BaseModel):
    category: str
    name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    client_api_version: str | None = None


class ExecuteCommandResponse(BaseModel):
    id: str
    status: CommandStatus
    reason: str | None = None
    queue_depth: int = 0


class CommandUpdatePayload(BaseModel):
    id: str
    state: CommandState
    timestamp: float
    sequence: int
    category: str
    name: str
    reason: str | None = None
    queue_depth: int = 0
    active_command_id: str | None = None
    result: dict[str, Any] | None = None


class CommandRecord(BaseModel):
    id: str
    category: str
    name: str
    state: CommandState
    sequence: int
    created_at: float
    updated_at: float
    queue_depth: int = 0
    reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None


class CommandHistoryResponse(BaseModel):
    items: list[CommandRecord] = Field(default_factory=list)
    total: int = 0
    active_command_id: str | None = None
    queue_depth: int = 0


class CapabilityResponse(BaseModel):
    api_version: str = "1.2.0"
    plugins: dict[str, PluginFeatureState] = Field(default_factory=dict)
    command_categories: list[str] = Field(default_factory=lambda: COMMAND_CATEGORIES.copy())
    transport: dict[str, str] = Field(default_factory=lambda: {
        "execute": "/execute",
        "state": "/state",
        "health": "/health",
        "capabilities": "/capabilities",
        "ws": "/ws",
        "commands": "/commands",
    })
