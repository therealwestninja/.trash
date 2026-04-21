from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_iso(): return datetime.now(UTC).isoformat()
def clamp01(v): return max(0.0, min(1.0, float(v)))

@dataclass
class HumanProfile:
    human_id: str
    name: str
    tier: str
    tags: list[str]
    familiarity: float = 0.2
    trust: float = 0.2
    comfort: float = 0.2
    affection: float = 0.2
    interaction_count: int = 0
    last_seen: str | None = None
    def dump(self): return self.__dict__.copy()

@dataclass
class State:
    humans: dict = field(default_factory=dict)
    best_friend_id: str | None = None
    recent_history: list[dict] = field(default_factory=list)
state = State()

def remember(entry):
    state.recent_history.append({"at": now_iso(), **entry}); state.recent_history = state.recent_history[-50:]

def _base_for_tier(tier: str):
    if tier == "best_friend": return 0.94,0.96,0.96,0.96
    if tier == "supporting": return 0.58,0.62,0.66,0.46
    return 0.15,0.10,0.20,0.05

def register_human(human_id, name, tier, tags):
    tier = tier.lower().strip()
    if tier not in {"best_friend","supporting","public"}: tier = "public"
    if tier == "best_friend":
        if state.best_friend_id and state.best_friend_id != human_id:
            prev = state.humans.get(state.best_friend_id)
            if prev: prev.tier = "supporting"
        state.best_friend_id = human_id
    if tier == "supporting":
        existing_support = [h for h in state.humans.values() if h.tier == "supporting" and h.human_id != human_id]
        if len(existing_support) >= 6:
            raise ValueError("supporting_human_limit_reached")
    fam, trust, comfort, affection = _base_for_tier(tier)
    existing = state.humans.get(human_id)
    if existing:
        existing.name = name or existing.name; existing.tier = tier; existing.tags = sorted(set(existing.tags + tags))
        existing.familiarity = max(existing.familiarity, fam if tier == "best_friend" else existing.familiarity)
        existing.trust = max(existing.trust, trust if tier == "best_friend" else existing.trust)
        existing.comfort = max(existing.comfort, comfort if tier == "best_friend" else existing.comfort)
        existing.affection = max(existing.affection, affection if tier == "best_friend" else existing.affection)
        remember({"event":"register_existing","human_id":human_id,"tier":tier}); return existing.dump()
    p = HumanProfile(human_id, name, tier, sorted(set(tags)), fam, trust, comfort, affection)
    state.humans[human_id] = p
    remember({"event":"register_new","human_id":human_id,"tier":tier})
    return p.dump()

def observe_human(human_id, event, closeness_m, tags):
    if human_id not in state.humans: register_human(human_id, human_id, "public", tags)
    p = state.humans[human_id]
    p.last_seen = now_iso(); p.interaction_count += 1; p.tags = sorted(set(p.tags + tags))
    if event == "positive_interaction":
        p.familiarity = clamp01(p.familiarity + 0.04); p.trust = clamp01(p.trust + 0.05); p.comfort = clamp01(p.comfort + 0.05)
        if p.tier != "public": p.affection = clamp01(p.affection + 0.04)
    elif event == "neutral_seen":
        p.familiarity = clamp01(p.familiarity + 0.01)
    elif event == "negative_interaction":
        p.trust = clamp01(p.trust - 0.08); p.comfort = clamp01(p.comfort - 0.06)
    if closeness_m is not None and closeness_m < 1.5 and p.tier != "public":
        p.comfort = clamp01(p.comfort + 0.02)
    remember({"event":"observe","human_id":human_id,"kind":event})
    return p.dump()

def update_relationship(human_id, familiarity_delta, trust_delta, comfort_delta, affection_delta):
    p = state.humans[human_id]
    p.familiarity = clamp01(p.familiarity + familiarity_delta)
    p.trust = clamp01(p.trust + trust_delta)
    p.comfort = clamp01(p.comfort + comfort_delta)
    p.affection = clamp01(p.affection + affection_delta)
    remember({"event":"manual_adjust","human_id":human_id})
    return p.dump()

def get_best_friend():
    p = state.humans.get(state.best_friend_id) if state.best_friend_id else None
    return p.dump() if p else None

def list_humans(): return [p.dump() for p in state.humans.values()]

def _score(p: HumanProfile, visible: bool):
    tier_bonus = {"best_friend":0.48,"supporting":0.24,"public":0.05}.get(p.tier, 0.0)
    visible_bonus = 0.15 if visible else 0.0
    return round(clamp01(tier_bonus + p.familiarity*0.18 + p.trust*0.18 + p.comfort*0.12 + p.affection*0.12 + visible_bonus), 6)

def rank_attention(visible_human_ids):
    visible = set(visible_human_ids)
    ranked = []
    for p in state.humans.values():
        item = p.dump(); item["attention_score"] = _score(p, p.human_id in visible)
        ranked.append(item)
    ranked.sort(key=lambda x: x["attention_score"], reverse=True)
    return ranked

def decay():
    for p in state.humans.values():
        if p.tier == "best_friend":
            d = 0.005
        elif p.tier == "supporting":
            d = 0.02
        else:
            d = 0.05
        p.familiarity = clamp01(p.familiarity - d)
        p.comfort = clamp01(p.comfort - d*0.6)
        if p.tier == "public": p.affection = clamp01(p.affection - d*0.4)
    remember({"event":"decay"})
    return status()

def reset():
    state.humans.clear(); state.best_friend_id = None; state.recent_history.clear()
    return status()

def status():
    return {"best_friend_id": state.best_friend_id, "human_count": len(state.humans), "supporting_count": sum(1 for p in state.humans.values() if p.tier == "supporting"), "public_count": sum(1 for p in state.humans.values() if p.tier == "public"), "recent_history": state.recent_history[-10:]}
