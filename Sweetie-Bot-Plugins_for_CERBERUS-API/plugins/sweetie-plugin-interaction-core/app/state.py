from dataclasses import dataclass

@dataclass
class InteractionState:
    engagement_target: str | None = None
    last_action: str | None = None
    friendliness: float = 0.8
    curiosity: float = 0.7

state = InteractionState()
