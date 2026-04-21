from dataclasses import dataclass, field
from datetime import datetime, UTC
from app.config import settings

def now_iso(): return datetime.now(UTC).isoformat()
def clamp01(v: float) -> float: return max(0.0, min(1.0, float(v)))

@dataclass
class State:
    episodes: list[dict] = field(default_factory=list)
    locations: dict = field(default_factory=dict)
    behavior_outcomes: list[dict] = field(default_factory=list)
    knowledge: list[dict] = field(default_factory=list)
    profile: dict = field(default_factory=lambda: {"trusted_locations":{}, "preferred_behaviors":{}, "important_tags":{}, "social_insights":{}, "autonomy_habits":{}})
state = State()

def ingest_episode(text, tags, salience, relationship_tier=None, autonomy_mode=None):
    e = {"at": now_iso(), "text": text, "tags": tags, "salience": clamp01(salience), "relationship_tier": relationship_tier, "autonomy_mode": autonomy_mode}
    state.episodes.append(e); state.episodes = state.episodes[-250:]
    return e

def ingest_location(name, position, confidence, metadata):
    entry = {"at": now_iso(), "position":{"x":float(position.get("x",0.0)),"y":float(position.get("y",0.0))}, "confidence": clamp01(confidence), "metadata": metadata}
    state.locations.setdefault(name, []).append(entry)
    state.locations[name] = state.locations[name][-120:]
    return {"name":name, **entry}

def ingest_behavior_outcome(behavior, reward, outcome, tags, relationship_tier=None, autonomy_mode=None):
    e = {"at": now_iso(), "behavior": behavior, "reward": max(-1.0, min(1.0, float(reward))), "outcome": outcome, "tags": tags, "relationship_tier": relationship_tier, "autonomy_mode": autonomy_mode}
    state.behavior_outcomes.append(e); state.behavior_outcomes = state.behavior_outcomes[-250:]
    return e

def _consolidate_locations():
    items = []
    for name, obs in state.locations.items():
        if len(obs) < settings.min_observations: continue
        avg_x = sum(o["position"]["x"] for o in obs)/len(obs)
        avg_y = sum(o["position"]["y"] for o in obs)/len(obs)
        avg_c = sum(o["confidence"] for o in obs)/len(obs)
        k = {"type":"stable_location","name":name,"position":{"x":round(avg_x,4),"y":round(avg_y,4)},"confidence": round(clamp01(avg_c+settings.location_confidence_bonus),6),"observations":len(obs)}
        items.append(k); state.profile["trusted_locations"][name] = k
    return items

def _consolidate_behaviors():
    grouped = {}
    for o in state.behavior_outcomes:
        grouped.setdefault(o["behavior"], []).append(o)
    items = []
    for beh, vals in grouped.items():
        if len(vals) < settings.min_observations: continue
        avg = sum(v["reward"] for v in vals)/len(vals)
        autonomy_modes = {}
        rel_tiers = {}
        for v in vals:
            if v.get("autonomy_mode"): autonomy_modes[v["autonomy_mode"]] = autonomy_modes.get(v["autonomy_mode"],0)+1
            if v.get("relationship_tier"): rel_tiers[v["relationship_tier"]] = rel_tiers.get(v["relationship_tier"],0)+1
        k = {"type":"preferred_behavior" if avg >= 0 else "discouraged_behavior","behavior":beh,"average_reward":round(avg,6),"confidence":round(clamp01((avg+1.0)/2.0+settings.behavior_confidence_bonus),6),"observations":len(vals),"autonomy_modes":autonomy_modes,"relationship_tiers":rel_tiers}
        items.append(k); state.profile["preferred_behaviors"][beh] = k
    return items

def _consolidate_tags():
    tags = {}
    social = {}
    autonomy = {}
    for e in state.episodes:
        rel_bonus = 0.25 if e.get("relationship_tier") == "best_friend" else (0.1 if e.get("relationship_tier") == "supporting" else 0.0)
        for tag in e["tags"]:
            tags[tag] = tags.get(tag, 0.0) + e["salience"] + rel_bonus
        if e.get("relationship_tier"):
            social[e["relationship_tier"]] = social.get(e["relationship_tier"],0) + e["salience"]
        if e.get("autonomy_mode"):
            autonomy[e["autonomy_mode"]] = autonomy.get(e["autonomy_mode"],0) + e["salience"]

    items = []
    for tag, score in sorted(tags.items(), key=lambda kv: kv[1], reverse=True):
        if score < 1.0: continue
        k = {"type":"important_tag","tag":tag,"score":round(score,6)}
        items.append(k); state.profile["important_tags"][tag] = k
    for tier, score in social.items():
        state.profile["social_insights"][tier] = {"tier": tier, "score": round(score,6)}
    for mode, score in autonomy.items():
        state.profile["autonomy_habits"][mode] = {"mode": mode, "score": round(score,6)}
    return items

def consolidate():
    state.knowledge.clear()
    state.profile = {"trusted_locations":{}, "preferred_behaviors":{}, "important_tags":{}, "social_insights":{}, "autonomy_habits":{}}
    locs = _consolidate_locations()
    behs = _consolidate_behaviors()
    tags = _consolidate_tags()
    state.knowledge.extend(locs); state.knowledge.extend(behs); state.knowledge.extend(tags)
    return {"knowledge": state.knowledge, "profile": state.profile, "counts":{"locations":len(locs),"behaviors":len(behs),"tags":len(tags)}}

def get_knowledge(): return state.knowledge
def get_profile(): return state.profile
def reset():
    state.episodes.clear(); state.locations.clear(); state.behavior_outcomes.clear(); state.knowledge.clear(); state.profile = {"trusted_locations":{}, "preferred_behaviors":{}, "important_tags":{}, "social_insights":{}, "autonomy_habits":{}}
    return status()
def status():
    return {"episode_count": len(state.episodes), "location_observation_groups": len(state.locations), "behavior_outcome_count": len(state.behavior_outcomes), "knowledge_count": len(state.knowledge), "profile": state.profile}
