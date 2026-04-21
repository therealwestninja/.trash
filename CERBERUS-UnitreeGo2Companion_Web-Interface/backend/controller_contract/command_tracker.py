from __future__ import annotations

import asyncio
import time
from collections import deque

from .models import CommandRecord, CommandRuntime, CommandState


class CommandTracker:
    def __init__(self, history_limit: int = 100) -> None:
        self._history: deque[CommandRecord] = deque(maxlen=history_limit)
        self._records: dict[str, CommandRecord] = {}
        self._active_command_id: str | None = None
        self._total_seen = 0
        self._sequence = 0
        self._queue_depth = 0
        self._worker_started = False
        self._lock = asyncio.Lock()

    async def mark_worker_started(self) -> None:
        async with self._lock:
            self._worker_started = True

    async def register(self, command_id: str, category: str, name: str, payload: dict, *, queue_depth: int) -> CommandRecord:
        async with self._lock:
            now = time.time()
            self._total_seen += 1
            self._sequence += 1
            record = CommandRecord(
                id=command_id,
                category=category,
                name=name,
                state=CommandState.QUEUED,
                sequence=self._sequence,
                created_at=now,
                updated_at=now,
                queue_depth=queue_depth,
                payload=payload,
            )
            self._records[command_id] = record
            self._history.append(record.model_copy(deep=True))
            self._queue_depth = queue_depth
            return record.model_copy(deep=True)

    async def update(
        self,
        command_id: str,
        state: CommandState,
        *,
        queue_depth: int,
        reason: str | None = None,
        result: dict | None = None,
    ) -> CommandRecord:
        async with self._lock:
            existing = self._records[command_id]
            updated = existing.model_copy(deep=True)
            updated.state = state
            updated.updated_at = time.time()
            updated.queue_depth = queue_depth
            if reason is not None:
                updated.reason = reason
            if result is not None:
                updated.result = result
            self._records[command_id] = updated
            self._replace_history(updated)
            self._queue_depth = queue_depth
            if state == CommandState.RUNNING:
                self._active_command_id = command_id
            elif self._active_command_id == command_id and state in {CommandState.COMPLETED, CommandState.FAILED}:
                self._active_command_id = None
            return updated.model_copy(deep=True)

    async def runtime(self) -> CommandRuntime:
        async with self._lock:
            last_id = self._history[-1].id if self._history else None
            return CommandRuntime(
                queue_depth=self._queue_depth,
                active_command_id=self._active_command_id,
                total_commands_seen=self._total_seen,
                last_command_id=last_id,
                worker_started=self._worker_started,
            )

    async def history(self, limit: int = 20) -> list[CommandRecord]:
        async with self._lock:
            items = list(self._history)[-limit:]
            return [item.model_copy(deep=True) for item in reversed(items)]

    async def get(self, command_id: str) -> CommandRecord | None:
        async with self._lock:
            record = self._records.get(command_id)
            return record.model_copy(deep=True) if record else None

    def _replace_history(self, updated: CommandRecord) -> None:
        replaced: deque[CommandRecord] = deque(maxlen=self._history.maxlen)
        found = False
        for item in self._history:
            if item.id == updated.id:
                replaced.append(updated.model_copy(deep=True))
                found = True
            else:
                replaced.append(item)
        if not found:
            replaced.append(updated.model_copy(deep=True))
        self._history = replaced
