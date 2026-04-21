from __future__ import annotations

import time
from typing import Any

from .models import SystemStatePayload


class StateManager:
    def __init__(self) -> None:
        self._state = SystemStatePayload()

    def get_state(self) -> SystemStatePayload:
        self._state.timestamp = time.time()
        return self._state

    def update_plugin_state(self, name: str, payload: dict[str, Any]) -> None:
        self._state.plugins[name] = payload


state_manager = StateManager()
