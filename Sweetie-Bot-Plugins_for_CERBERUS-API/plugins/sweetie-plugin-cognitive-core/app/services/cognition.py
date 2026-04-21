from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_iso():
    return datetime.now(UTC).isoformat()

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

@dataclass
class State:
    mood: str = "curious"
    curiosity: float = 0.8
    sociability: float = 0.85
    caution: float = 0.45
    attention_target: dict | None = None
    current_goal: str | None = None
    recent_reasoning: list[dict] = field(default_factory=list)

state = State()

def remember(stage: str, result: dict):
    state.recent_reasoning.append({"at": now_iso(), "stage": stage, "result": result})
    state.recent_reasoning = state.recent_reasoning[-30:]

def interpret_event(event: dict) -> dict:
    topic = event.get("topic", "")
    payload = event.get("payload", {}) or {}
    tags = payload.get("tags", []) or []
    if topic.startswith("vision.person_"):
        intent = "engage_operator" if "operator" in tags else "observe_person"
        goal = "social_attention"
    elif topic.startswith("vision.hazard"):
        intent = "avoid_hazard"
        goal = "preserve_safety"
    elif topic.startswith("vision.scene_update"):
        intent = "refresh_scene_context"
        goal = "maintain_environment_model"
    else:
        intent = "observe"
        goal = "maintain_awareness"
    score = 0.55 + (0.2 if "operator" in tags else 0.0) + (0.1 if topic.startswith("vision.person_") else 0.0)
    score = min(1.0, score)
    result = {"intent": intent, "goal": goal, "attention_score": round(score,4), "event": event}
    if score >= 0.6:
        state.attention_target = payload
        state.current_goal = goal
    remember("interpret_event", result)
    return result

def evaluate_context(context: dict) -> dict:
    result = {
        "mood": state.mood,
        "current_goal": state.current_goal,
        "attention_target": state.attention_target,
        "battery": context.get("battery", 1.0),
        "operator_visible": context.get("operator_visible", False),
    }
    remember("evaluate_context", result)
    return result

def set_state_fields(data: dict) -> dict:
    if data.get("mood") is not None:
        state.mood = str(data["mood"])
    for k in ["curiosity", "sociability", "caution"]:
        if data.get(k) is not None:
            setattr(state, k, clamp01(data[k]))
    return dump_state()

def dump_state():
    return {
        "mood": state.mood,
        "curiosity": state.curiosity,
        "sociability": state.sociability,
        "caution": state.caution,
        "attention_target": state.attention_target,
        "current_goal": state.current_goal,
        "recent_reasoning": state.recent_reasoning[-10:],
    }

def reset_state():
    state.mood = "curious"
    state.curiosity = 0.8
    state.sociability = 0.85
    state.caution = 0.45
    state.attention_target = None
    state.current_goal = None
    state.recent_reasoning.clear()
    return dump_state()
