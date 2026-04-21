from __future__ import annotations

from .event_helpers import make_event
from .event_stream import event_stream


async def publish_runtime_bundle(state: dict) -> None:
    await event_stream.broadcast_json(make_event("runtime_state", state))
    if state.get("command_mux") is not None:
        await event_stream.broadcast_json(make_event("control_source", state.get("command_mux")))
    if state.get("diagnostics") is not None:
        await event_stream.broadcast_json(make_event("diagnostics", state.get("diagnostics")))
    if state.get("lifecycle") is not None:
        await event_stream.broadcast_json(make_event("lifecycle", state.get("lifecycle")))


async def publish_session_bundle(session_state: dict | None, lifecycle_state: dict | None = None) -> None:
    await event_stream.broadcast_json(make_event("session_state", session_state or {}))
    if lifecycle_state is not None:
        await event_stream.broadcast_json(make_event("lifecycle", lifecycle_state))


async def publish_named_event(event_type: str, data: dict | None = None) -> None:
    await event_stream.broadcast_json(make_event(event_type, data or {}))
