from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class SessionSnapshot:
    active: bool
    operator_id: str | None
    active_connections: int


class SessionManager:
    def __init__(self) -> None:
        self._operator_id: str | None = None
        self._connections = 0
        self._lock = asyncio.Lock()

    async def connect(self, operator_id: str | None = None) -> SessionSnapshot:
        async with self._lock:
            self._connections += 1
            if operator_id and not self._operator_id:
                self._operator_id = operator_id
            return self.snapshot()

    async def disconnect(self) -> SessionSnapshot:
        async with self._lock:
            self._connections = max(0, self._connections - 1)
            if self._connections == 0:
                self._operator_id = None
            return self.snapshot()

    def activate(self, operator_id: str = 'local-operator') -> None:
        self._operator_id = operator_id

    def deactivate(self) -> None:
        self._operator_id = None

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            active=self._operator_id is not None,
            operator_id=self._operator_id,
            active_connections=self._connections,
        )
