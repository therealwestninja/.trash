from dataclasses import dataclass, field

@dataclass
class State:
    engagement_target: str | None = None
    last_action: str | None = None
    friendliness: float = 0.82
    curiosity: float = 0.78
    recent_interactions: list[dict] = field(default_factory=list)

state = State()
