from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.config import settings

def now_iso(): return datetime.now(UTC).isoformat()
def clamp01(v: float) -> float: return max(0.0, min(1.0, float(v)))

@dataclass
class State:
    curiosity: float = 0.80
    caution: float = 0.40
    affection: float = 0.78
    confidence: float = 0.72
    behavior_scores: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)
state = State()

def _behavior_score(name: str) -> float: return float(state.behavior_scores.get(name, 0.5))
def _set_behavior_score(name: str, value: float): state.behavior_scores[name] = round(clamp01(value), 6)

def _decay_behaviors():
    for k,v in list(state.behavior_scores.items()):
        neutral = 0.5
        if v > neutral: v = max(neutral, v - settings.decay_rate)
        elif v < neutral: v = min(neutral, v + settings.decay_rate)
        state.behavior_scores[k] = round(v,6)

def record_outcome(behavior, outcome, reward, tags, notes, relationship_tier=None, autonomy_mode=None):
    reward = max(-1.0, min(1.0, float(reward)))
    _decay_behaviors()
    if relationship_tier == "best_friend": reward *= 1.15
    if autonomy_mode in {"dock_seek","dock_urgent"} and behavior == "seek_dock": reward *= 1.10
    if autonomy_mode == "safe_stop" and reward < 0: reward *= 0.5

    current = _behavior_score(behavior)
    _set_behavior_score(behavior, current + (reward * settings.learning_rate))

    if reward > 0:
        state.confidence = clamp01(state.confidence + reward * 0.05)
        if relationship_tier in {"best_friend","supporting"} or "social" in tags:
            state.affection = clamp01(state.affection + reward * 0.03)
        if "novel" in tags or "explore" in tags:
            state.curiosity = clamp01(state.curiosity + reward * 0.02)
        if autonomy_mode in {"dock_seek","dock_urgent","charging"}:
            state.caution = clamp01(state.caution + 0.005)
        else:
            state.caution = clamp01(state.caution - reward * 0.015)
    elif reward < 0:
        mag = abs(reward)
        state.caution = clamp01(state.caution + mag * 0.05)
        state.confidence = clamp01(state.confidence - mag * 0.04)
        if relationship_tier == "best_friend" and outcome in {"rejected","ignored","failure"}:
            state.affection = clamp01(state.affection - mag * 0.01)

    entry = {
        "at": now_iso(),
        "behavior": behavior,
        "outcome": outcome,
        "reward": reward,
        "tags": tags,
        "notes": notes,
        "relationship_tier": relationship_tier,
        "autonomy_mode": autonomy_mode,
        "behavior_score": state.behavior_scores[behavior],
        "profile_after": get_profile(),
    }
    state.history.append(entry); state.history = state.history[-120:]
    return entry

def adjust_traits(data):
    for field in ["curiosity","caution","affection","confidence"]:
        if data.get(field) is not None: setattr(state, field, clamp01(data[field]))
    return get_profile()

def get_profile():
    return {
        "curiosity": round(state.curiosity,6),
        "caution": round(state.caution,6),
        "affection": round(state.affection,6),
        "confidence": round(state.confidence,6),
        "behavior_scores": dict(sorted(state.behavior_scores.items(), key=lambda kv: kv[1], reverse=True)[:12]),
    }

def get_history(limit=25): return state.history[-limit:]

def reset():
    state.curiosity=0.80; state.caution=0.40; state.affection=0.78; state.confidence=0.72; state.behavior_scores.clear(); state.history.clear()
    return get_profile()

def status():
    return {"profile": get_profile(), "history_count": len(state.history)}
