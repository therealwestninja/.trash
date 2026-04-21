from dataclasses import dataclass, field
from typing import Any


@dataclass
class PresenceRuntime:
    idle_counter: int = 0
    last: dict[str, Any] = field(default_factory=dict)

    def tick(self, emotion: dict[str, float]) -> dict[str, Any]:
        self.idle_counter += 1

        curiosity = float(emotion.get("curiosity", 0.0))
        stress = float(emotion.get("stress", 0.0))

        if stress >= 0.7:
            behavior = "idle_guard"
        elif curiosity >= 0.6:
            behavior = "idle_scan"
        else:
            behavior = "idle_breathe"

        self.last = {
            "idle_behavior": behavior,
            "idle_counter": self.idle_counter,
        }
        return self.last
