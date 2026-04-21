from __future__ import annotations

import json
from time import time
from typing import Any


class SessionRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.is_recording: bool = True

    def record(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self.is_recording:
            return
        self.events.append({
            "timestamp": time(),
            "type": event_type,
            "payload": payload,
        })
        self.events = self.events[-500:]

    def export_jsonl(self) -> str:
        return "\n".join(json.dumps(event, ensure_ascii=False) for event in self.events)

    def snapshot(self) -> dict[str, Any]:
        return {
            "is_recording": self.is_recording,
            "event_count": len(self.events),
            "latest_event": self.events[-1] if self.events else None,
        }

    def clear(self) -> None:
        self.events.clear()


session_recorder = SessionRecorder()
