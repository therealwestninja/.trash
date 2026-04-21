from __future__ import annotations

import time

from .bridges import BaseControlBridge
from .command_tracker import CommandTracker
from .models import BridgeState, HardwareState, RobotState, SessionState, SimulationState, SystemStatePayload
from .plugin_registry import PluginRegistry
from .safety_manager import SafetyManager
from .session_manager import SessionManager


class StateManager:
    def __init__(
        self,
        bridge: BaseControlBridge,
        session_manager: SessionManager,
        safety_manager: SafetyManager,
        plugin_registry: PluginRegistry,
        command_tracker: CommandTracker,
        *,
        api_version: str = '1.2.0',
    ) -> None:
        self.bridge = bridge
        self.session_manager = session_manager
        self.safety_manager = safety_manager
        self.plugin_registry = plugin_registry
        self.command_tracker = command_tracker
        self.api_version = api_version

    async def get_state(self) -> SystemStatePayload:
        telemetry = await self.bridge.get_telemetry()
        policy = self.safety_manager.policy(telemetry)
        session = self.session_manager.snapshot()
        runtime = await self.command_tracker.runtime()
        return SystemStatePayload(
            api_version=self.api_version,
            hardware=HardwareState(mode=self.bridge.hardware_mode),
            robot=RobotState(platform='unitree_go2'),
            bridge=BridgeState(connected=self.bridge.connected),
            session=SessionState(
                active=session.active,
                operator_id=session.operator_id,
                active_connections=session.active_connections,
            ),
            command_policy=policy,
            simulation=SimulationState(active=self.bridge.hardware_mode.value == 'simulation'),
            telemetry=telemetry,
            plugins=self.plugin_registry.get_capabilities(),
            command_runtime=runtime,
            timestamp=time.time(),
        )

    async def get_health(self) -> dict:
        state = await self.get_state()
        return {
            'ok': state.bridge.connected,
            'api_version': state.api_version,
            'hardware_mode': state.hardware.mode,
            'session_active': state.session.active,
            'restricted': state.command_policy.restricted,
            'queue_depth': state.command_runtime.queue_depth,
            'active_command_id': state.command_runtime.active_command_id,
            'timestamp': state.timestamp,
        }

    async def get_capabilities(self) -> dict:
        state = await self.get_state()
        return {
            'api_version': state.api_version,
            'plugins': state.plugins,
            'command_categories': state.command_policy.allowed_categories,
            'transport': {
                'execute': '/execute',
                'state': '/state',
                'health': '/health',
                'capabilities': '/capabilities',
                'ws': '/ws',
                'commands': '/commands',
            },
        }
