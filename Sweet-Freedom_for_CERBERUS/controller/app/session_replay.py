from __future__ import annotations

import json
from time import time
from typing import Any


class SessionReplay:
    def __init__(self) -> None:
        self.loaded_events: list[dict[str, Any]] = []
        self.cursor: int = 0
        self.is_loaded: bool = False
        self.started_at: float | None = None

    def load_jsonl(self, text: str) -> dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        self.loaded_events = [json.loads(line) for line in lines]
        self.cursor = 0
        self.is_loaded = True
        self.started_at = None
        return self.snapshot()

    def clear(self) -> dict[str, Any]:
        self.loaded_events = []
        self.cursor = 0
        self.is_loaded = False
        self.started_at = None
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "is_loaded": self.is_loaded,
            "cursor": self.cursor,
            "event_count": len(self.loaded_events),
            "next_event": self.loaded_events[self.cursor] if self.is_loaded and self.cursor < len(self.loaded_events) else None,
            "started_at": self.started_at,
        }

    def step(self) -> dict[str, Any] | None:
        if not self.is_loaded or self.cursor >= len(self.loaded_events):
            return None
        event = self.loaded_events[self.cursor]
        self.cursor += 1
        if self.started_at is None:
            self.started_at = time()
        return event


session_replay = SessionReplay()
