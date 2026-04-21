from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_iso():
    return datetime.now(UTC).isoformat()

@dataclass
class State:
    events: list[dict] = field(default_factory=list)

state = State()

def inject_best_friend(payload: dict):
    event = {
        "at": now_iso(),
        "topic": "vision.person_detected",
        "payload": {
            "track_id": payload.get("human_id", "dev-001"),
            "label": "person",
            "tags": ["operator", "best_friend"],
            "relationship_tier": "best_friend",
            "distance_m": payload.get("distance_m", 1.2)
        }
    }
    state.events.append(event)
    state.events = state.events[-50:]
    return event

def inject_public_person(payload: dict):
    event = {
        "at": now_iso(),
        "topic": "vision.person_detected",
        "payload": {
            "track_id": payload.get("human_id", "public-001"),
            "label": "person",
            "tags": ["public"],
            "relationship_tier": "public",
            "distance_m": payload.get("distance_m", 2.5)
        }
    }
    state.events.append(event)
    state.events = state.events[-50:]
    return event

def get_state():
    return {"recent_events": state.events[-10:]}
