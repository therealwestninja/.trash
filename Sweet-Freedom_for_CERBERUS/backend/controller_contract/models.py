from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class HardwareMode(str, Enum):
    REAL = "real"
    SIMULATION = "simulation"


class CommandState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


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


class TelemetryPayload(BaseModel):
    battery_level: float = 100.0
    motion_state: str = "idle"
    position: dict[str, float] = Field(
        default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0}
    )
    docking_state: str = "undocked"
    safety_flags: list[str] = Field(default_factory=list)


class CommandRuntime(BaseModel):
    queue_depth: int = 0
    active_command_id: str | None = None
    total_commands_seen: int = 0
    last_command_state: CommandState | None = None


class SystemStatePayload(BaseModel):
    api_version: str = "0.2.0"
    hardware: HardwareState = Field(default_factory=HardwareState)
    robot: RobotState = Field(default_factory=RobotState)
    bridge: BridgeState = Field(default_factory=BridgeState)
    session: SessionState = Field(default_factory=SessionState)
    telemetry: TelemetryPayload = Field(default_factory=TelemetryPayload)
    plugins: dict[str, Any] = Field(default_factory=dict)
    command_runtime: CommandRuntime = Field(default_factory=CommandRuntime)
    timestamp: float = 0.0
