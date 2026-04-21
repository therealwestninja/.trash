from __future__ import annotations

from dataclasses import dataclass, asdict
from time import time


@dataclass
class CommandSource:
    name: str
    priority: int
    locked: bool = False
    last_seen: float = 0.0


class CommandMux:
    def __init__(self) -> None:
        self.sources = {
            "safety": CommandSource(name="safety", priority=100),
            "ui": CommandSource(name="ui", priority=80),
            "quick_action": CommandSource(name="quick_action", priority=70),
            "autonomy": CommandSource(name="autonomy", priority=60),
        }
        self.active_source = "ui"

    def touch(self, source_name: str) -> None:
        if source_name not in self.sources:
            self.sources[source_name] = CommandSource(name=source_name, priority=50)
        self.sources[source_name].last_seen = time()

    def can_accept(self, source_name: str) -> tuple[bool, str]:
        self.touch(source_name)
        candidate = self.sources[source_name]
        active = self.sources.get(self.active_source)

        if candidate.locked:
            return False, f"source '{source_name}' is locked"

        if active and active.name != source_name and active.locked and active.priority >= candidate.priority:
            return False, f"active source '{active.name}' is locked"

        if active and active.name != source_name and active.priority > candidate.priority:
            return False, f"active source '{active.name}' outranks '{source_name}'"

        self.active_source = source_name
        return True, "accepted"

    def lock(self, source_name: str) -> bool:
        if source_name not in self.sources:
            return False
        self.sources[source_name].locked = True
        return True

    def unlock(self, source_name: str) -> bool:
        if source_name not in self.sources:
            return False
        self.sources[source_name].locked = False
        return True

    def snapshot(self) -> dict:
        return {
            "active_source": self.active_source,
            "sources": {name: asdict(source) for name, source in self.sources.items()},
        }
