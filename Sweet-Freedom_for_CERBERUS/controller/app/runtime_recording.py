from __future__ import annotations

from typing import Any

from .session_recorder import session_recorder


def record_runtime_event(event_type: str, payload: dict[str, Any]) -> None:
    session_recorder.record(event_type, payload)
