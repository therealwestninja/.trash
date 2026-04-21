from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque

from .bridges import BaseControlBridge
from .command_tracker import CommandTracker
from .event_bus import EventBus
from .models import CommandState, CommandStatus, CommandUpdatePayload, ExecuteCommandRequest, ExecuteCommandResponse
from .safety_manager import SafetyManager
from .state_manager import StateManager


class CommandRouter:
    def __init__(
        self,
        bridge: BaseControlBridge,
        state_manager: StateManager,
        safety_manager: SafetyManager,
        event_bus: EventBus,
        command_tracker: CommandTracker,
        *,
        duplicate_window: int = 25,
        min_command_interval_s: float = 0.2,
    ) -> None:
        self.bridge = bridge
        self.state_manager = state_manager
        self.safety_manager = safety_manager
        self.event_bus = event_bus
        self.command_tracker = command_tracker
        self._recent: deque[tuple[str, float]] = deque(maxlen=duplicate_window)
        self._min_command_interval_s = min_command_interval_s
        self._last_command_at = 0.0
        self._queue: asyncio.Queue[tuple[str, ExecuteCommandRequest]] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._worker_task is None:
            await self.command_tracker.mark_worker_started()
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    async def enqueue(self, request: ExecuteCommandRequest) -> ExecuteCommandResponse:
        state = await self.state_manager.get_state()
        response_id = self._command_id()
        if request.client_api_version and request.client_api_version != state.api_version:
            return ExecuteCommandResponse(id=response_id, status=CommandStatus.REJECTED, reason='client_api_version_mismatch')
        if request.category not in state.command_policy.allowed_categories:
            return ExecuteCommandResponse(id=response_id, status=CommandStatus.REJECTED, reason='category_not_allowed')
        if time.time() - self._last_command_at < self._min_command_interval_s:
            return ExecuteCommandResponse(id=response_id, status=CommandStatus.REJECTED, reason='rate_limit_exceeded')
        signature = f"{request.category}:{request.name}:{sorted(request.payload.items())}"
        if any(sig == signature for sig, _ in self._recent):
            return ExecuteCommandResponse(id=response_id, status=CommandStatus.REJECTED, reason='duplicate_command_suppressed')

        self._last_command_at = time.time()
        self._recent.append((signature, self._last_command_at))
        await self._queue.put((response_id, request))
        record = await self.command_tracker.register(
            response_id,
            request.category,
            request.name,
            request.payload,
            queue_depth=self._queue.qsize(),
        )
        await self._publish_record(record)
        return ExecuteCommandResponse(
            id=response_id,
            status=CommandStatus.ACCEPTED,
            queue_depth=self._queue.qsize(),
        )

    async def _worker_loop(self) -> None:
        while True:
            command_id, request = await self._queue.get()
            try:
                running = await self.command_tracker.update(
                    command_id,
                    CommandState.RUNNING,
                    queue_depth=self._queue.qsize(),
                )
                await self._publish_record(running)
                result = await self.bridge.execute(request.category, request.name, request.payload)
                completed = await self.command_tracker.update(
                    command_id,
                    CommandState.COMPLETED,
                    queue_depth=self._queue.qsize(),
                    result=result,
                )
                await self._publish_record(completed)
                state = await self.state_manager.get_state()
                await self.event_bus.publish('system_state', state.model_dump(mode='json'))
                await self.event_bus.publish('telemetry', state.telemetry.model_dump())
                for fault in self.safety_manager.active_faults:
                    await self.event_bus.publish('fault', fault.model_dump())
            except Exception as exc:
                failed = await self.command_tracker.update(
                    command_id,
                    CommandState.FAILED,
                    queue_depth=self._queue.qsize(),
                    reason=str(exc),
                )
                await self._publish_record(failed)
            finally:
                self._queue.task_done()

    async def _publish_record(self, record) -> None:
        payload = CommandUpdatePayload(
            id=record.id,
            state=record.state,
            timestamp=record.updated_at,
            sequence=record.sequence,
            category=record.category,
            name=record.name,
            reason=record.reason,
            queue_depth=record.queue_depth,
            active_command_id=(await self.command_tracker.runtime()).active_command_id,
            result=record.result,
        )
        await self.event_bus.publish('command_update', payload.model_dump(mode='json'))

    @staticmethod
    def _command_id() -> str:
        return f'cmd_{uuid.uuid4().hex[:12]}'
