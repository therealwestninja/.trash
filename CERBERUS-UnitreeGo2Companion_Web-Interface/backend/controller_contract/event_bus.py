from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Awaitable, Callable

from fastapi import WebSocket

from .models import EventEnvelope

Subscriber = Callable[[EventEnvelope], Awaitable[None]]


class EventBus:
    def __init__(self, replay_limit: int = 50) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._clients: set[WebSocket] = set()
        self._replay: deque[EventEnvelope] = deque(maxlen=replay_limit)
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: str, subscriber: Subscriber) -> None:
        self._subscribers[event_type].append(subscriber)

    async def register_client(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)

    async def unregister_client(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)

    async def publish(self, event_type: str, payload: dict) -> EventEnvelope:
        envelope = EventEnvelope(type=event_type, timestamp=time.time(), payload=payload)
        self._replay.append(envelope)
        for subscriber in list(self._subscribers.get(event_type, [])):
            await subscriber(envelope)
        await self.broadcast(envelope)
        return envelope

    async def broadcast(self, envelope: EventEnvelope) -> None:
        if not self._clients:
            return
        dead: list[WebSocket] = []
        message = envelope.model_dump_json()
        async with self._lock:
            clients = list(self._clients)
        for client in clients:
            try:
                await client.send_text(message)
            except Exception:
                dead.append(client)
        if dead:
            async with self._lock:
                for client in dead:
                    self._clients.discard(client)

    async def send_snapshot(self, websocket: WebSocket, payload: dict) -> None:
        envelope = EventEnvelope(type='snapshot', timestamp=time.time(), payload=payload)
        await websocket.send_text(envelope.model_dump_json())

    async def replay_recent(self, websocket: WebSocket, limit: int = 10) -> None:
        for envelope in list(self._replay)[-limit:]:
            await websocket.send_text(envelope.model_dump_json())

    async def broadcast_heartbeat(self) -> None:
        await self.publish('heartbeat', {'status': 'ok'})
