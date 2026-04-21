from dataclasses import dataclass
from typing import Any


@dataclass
class AnimationRuntime:
    current_clip: str = "idle_breathe"
    playing: bool = False

    def resolve_for_expression(self, expression_payload: dict[str, Any]) -> dict[str, Any]:
        expression = expression_payload.get("expression", "calm")
        mapping = {
            "happy": "happy_trot",
            "curious": "curious_scan",
            "guarded": "idle_guard",
            "calm": "idle_breathe",
        }

        clip = mapping.get(expression, "idle_breathe")
        self.current_clip = clip
        self.playing = True

        return {
            "current_clip": clip,
            "playing": self.playing,
        }
