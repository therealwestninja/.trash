from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.config import settings

def now_iso(): return datetime.now(UTC).isoformat()
def clamp01(v: float) -> float: return max(0.0, min(1.0, float(v)))

@dataclass
class State:
    novelty_weight: float = settings.novelty_weight
    social_weight: float = settings.social_weight
    salience_weight: float = settings.salience_weight
    candidates: dict = field(default_factory=dict)
    current_focus: dict | None = None
    focus_history: list[dict] = field(default_factory=list)
state = State()

def _relationship_bonus(tier: str | None) -> float:
    if tier == "best_friend": return 0.35
    if tier == "supporting": return 0.18
    if tier == "public": return 0.03
    return 0.0

def _kind_bonus(kind: str) -> float:
    if kind == "peer_robot": return 0.12
    if kind == "human": return 0.10
    return 0.0

def _distance_modifier(d: float) -> float:
    if d <= 0: return 1.0
    if d < 1.0: return 1.0
    if d < 2.0: return 0.9
    if d < 4.0: return 0.75
    return 0.55

def score_candidate(candidate: dict, autonomy_mode: str | None = None) -> float:
    base = (
        clamp01(candidate.get("novelty",0.0))*state.novelty_weight
        + clamp01(candidate.get("salience",0.5))*state.salience_weight
        + clamp01(candidate.get("confidence",0.5))*0.1
        + clamp01(candidate.get("persistence",0.0))*0.1
    )
    social = state.social_weight + _relationship_bonus(candidate.get("relationship_tier")) + _kind_bonus(candidate.get("target_kind","entity"))
    base += social * (0.25 if candidate.get("label") == "person" or candidate.get("target_kind") in {"human","peer_robot"} else 0.05)
    base *= _distance_modifier(float(candidate.get("distance_m",0.0)))

    if autonomy_mode == "follow_operator" and candidate.get("relationship_tier") == "best_friend":
        base += 0.18
    if autonomy_mode in {"dock_seek","dock_urgent"} and candidate.get("label") == "charging_dock":
        base += 0.22
    if autonomy_mode == "social" and candidate.get("target_kind") == "human":
        base += 0.12
    return round(clamp01(base), 6)

def ingest_candidates(candidates: list[dict], autonomy_mode: str | None = None):
    ranked = []
    for raw in candidates:
        tid = raw["target_id"]
        if tid in state.candidates:
            prev = state.candidates[tid]
            raw["persistence"] = round(min(1.0, float(prev.get("persistence",0.0)) + 0.2), 4)
        else:
            raw["persistence"] = round(float(raw.get("persistence",0.0)),4)
        raw["attention_score"] = score_candidate(raw, autonomy_mode)
        state.candidates[tid] = raw
        ranked.append(raw)
    ranked.sort(key=lambda x: x["attention_score"], reverse=True)
    return ranked

def rank_candidates(autonomy_mode: str | None = None):
    ranked = []
    for tid, cand in list(state.candidates.items()):
        cand["attention_score"] = score_candidate(cand, autonomy_mode)
        ranked.append(cand)
    ranked.sort(key=lambda x: x["attention_score"], reverse=True)
    return ranked

def select_focus(autonomy_mode: str | None = None):
    ranked = rank_candidates(autonomy_mode)
    if not ranked:
        state.current_focus = None
        return None
    selected = ranked[0]
    prev = state.current_focus
    if prev and prev.get("target_id") != selected.get("target_id"):
        if float(selected.get("attention_score",0.0)) < float(prev.get("attention_score",0.0)) + 0.12:
            selected = prev
    state.current_focus = selected
    state.focus_history.append({"at": now_iso(), "focus": selected, "autonomy_mode": autonomy_mode})
    state.focus_history = state.focus_history[-25:]
    return selected

def set_bias(data: dict):
    for k in ["novelty_weight","social_weight","salience_weight"]:
        if data.get(k) is not None:
            setattr(state, k, clamp01(data[k]))
    return status()

def status():
    return {
        "novelty_weight": state.novelty_weight,
        "social_weight": state.social_weight,
        "salience_weight": state.salience_weight,
        "candidate_count": len(state.candidates),
        "current_focus": state.current_focus,
        "recent_focus_history": state.focus_history[-10:],
    }

def reset():
    state.candidates.clear()
    state.current_focus = None
    state.focus_history.clear()
    return {"reset": True}
