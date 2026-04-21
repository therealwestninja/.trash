from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExpressionRuntime:
    current_expression: str = "calm"
    history: list[dict[str, Any]] = field(default_factory=list)

    def resolve(self, emotion: dict[str, float], presence: dict[str, Any]) -> dict[str, Any]:
        valence = float(emotion.get("valence", 0.5))
        curiosity = float(emotion.get("curiosity", 0.0))
        stress = float(emotion.get("stress", 0.0))
        idle_behavior = presence.get("idle_behavior", "idle_breathe")

        if stress >= 0.7:
            expression = "guarded"
            movement_style = "stiff"
        elif curiosity >= 0.6:
            expression = "curious"
            movement_style = "attentive"
        elif valence >= 0.65:
            expression = "happy"
            movement_style = "light"
        else:
            expression = "calm"
            movement_style = "smooth"

        payload = {
            "expression": expression,
            "movement_style": movement_style,
            "idle_behavior": idle_behavior,
        }
        self.current_expression = expression
        self.history.append(payload)
        return payload
