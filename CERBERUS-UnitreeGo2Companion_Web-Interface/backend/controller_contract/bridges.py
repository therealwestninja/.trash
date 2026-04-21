from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from .models import HardwareMode, TelemetryPayload


@dataclass
class BridgeTelemetry:
    battery_level: float = 100.0
    motion_state: str = 'idle'
    position: dict[str, float] = field(default_factory=lambda: {'x': 0.0, 'y': 0.0, 'yaw': 0.0})
    docking_state: str = 'undocked'
    safety_flags: list[str] = field(default_factory=list)


class BaseControlBridge:
    hardware_mode: HardwareMode = HardwareMode.SIMULATION
    connected: bool = False

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def get_telemetry(self) -> TelemetryPayload:
        raise NotImplementedError

    async def execute(self, category: str, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class SimulationControlBridge(BaseControlBridge):
    hardware_mode = HardwareMode.SIMULATION

    def __init__(self) -> None:
        self.connected = True
        self._telemetry = BridgeTelemetry()

    async def get_telemetry(self) -> TelemetryPayload:
        return TelemetryPayload(**self._telemetry.__dict__)

    async def execute(self, category: str, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(0.02)
        if category == 'motion':
            self._telemetry.motion_state = name
            if name == 'move':
                self._telemetry.position['x'] += float(payload.get('vx', 0.0))
                self._telemetry.position['y'] += float(payload.get('vy', 0.0))
                self._telemetry.position['yaw'] += float(payload.get('vyaw', 0.0))
        elif category == 'always' and name == 'stop':
            self._telemetry.motion_state = 'stopped'
        elif category == 'mission':
            self._telemetry.motion_state = f'mission:{name}'
        elif category == 'plugin':
            self._telemetry.motion_state = f'plugin:{name}'
        self._telemetry.battery_level = max(0.0, self._telemetry.battery_level - 0.05)
        return {'ok': True, 'category': category, 'name': name, 'payload': payload}
