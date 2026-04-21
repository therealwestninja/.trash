from dataclasses import dataclass, field
from datetime import datetime, UTC

def now_iso(): return datetime.now(UTC).isoformat()
def clamp01(v: float) -> float: return max(0.0, min(1.0, float(v)))

@dataclass
class State:
    energy: float = 0.82
    curiosity: float = 0.86
    affection: float = 0.80
    drama: float = 0.42
    caution: float = 0.38
    mood: str = "bubbly"
    recent_behaviors: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
state = State()

def remember(intent: str, result: dict):
    state.recent_behaviors.append({"at": now_iso(), "intent": intent, "result": result})
    state.recent_behaviors = state.recent_behaviors[-25:]

def tone_from_context(context: dict):
    mode = context.get("autonomy_mode")
    tier = context.get("relationship_tier")
    if mode == "charging": return "soft_careful"
    if mode in {"dock_seek","dock_urgent"}: return "soft_careful"
    if tier == "best_friend": return "bright_cheerful"
    if context.get("peer_context"): return "warm_playful"
    if state.drama > 0.7: return "dramatic_cute"
    return "warm_playful"

def speech_for(intent: str, context: dict):
    tier = context.get("relationship_tier")
    if intent == "engage_operator":
        return "Ooo! There you are! I'll come with you!"
    if intent == "follow_operator":
        return "Okay! I'm right behind you!"
    if intent == "observe_person":
        return "Hi! I see somepony over there."
    if intent == "explore_novel_object":
        return "Oh! What's that? Can we check it out?"
    if intent == "avoid_hazard":
        return "Eep! Better be careful."
    if intent == "peer_checkin":
        return "Cutie Mark Crusaders status check!"
    if intent == "dock_seek":
        return "I should go charge up a little."
    if tier == "public":
        return "Hello!"
    return "Hmm... I wonder what we should do next."

def behavior_mode(intent: str, context: dict):
    mode = context.get("autonomy_mode")
    if mode in {"dock_seek","dock_urgent"}: return "careful_return"
    if intent == "engage_operator": return "excited_follow"
    if intent == "follow_operator": return "loyal_follow"
    if intent == "observe_person": return "friendly_observe"
    if intent == "explore_novel_object": return "curious_investigate"
    if intent == "peer_checkin": return "team_sync"
    return "bubbly_idle"

def movement_style(intent: str, context: dict):
    mode = context.get("autonomy_mode")
    if mode in {"dock_seek","dock_urgent"}: return "careful_trot"
    if intent in {"engage_operator","follow_operator"}: return "light_trot"
    if intent == "explore_novel_object": return "curious_prance"
    return "gentle_step"

def process_intent(intent: str, context: dict):
    if context.get("battery",1.0) < 0.2:
        state.mood = "tired_but_sweet"
    elif context.get("relationship_tier") == "best_friend":
        state.mood = "excited"
    elif context.get("peer_context"):
        state.mood = "teamwork"
    elif intent == "avoid_hazard":
        state.mood = "nervous"
    else:
        state.mood = "curious"

    result = {
        "behavior_mode": behavior_mode(intent, context),
        "tone": tone_from_context(context),
        "speech": speech_for(intent, context),
        "movement_style": movement_style(intent, context),
        "attention_bias": "operator_locked" if context.get("relationship_tier") == "best_friend" else ("squad_sync" if context.get("peer_context") else "balanced"),
        "mood": state.mood,
        "character_envelope": {
            "style_tags": ["wholesome","playful","youthful","expressive"],
            "energy": round(state.energy,3),
            "curiosity": round(state.curiosity,3),
            "affection": round(state.affection,3),
            "drama": round(state.drama,3),
            "caution": round(state.caution,3),
        },
    }
    remember(intent, result)
    return result

def generate_style(action_name: str, context: dict):
    mapping = {
        "follow_operator":"follow_operator",
        "observe_person":"observe_person",
        "idle_scan":"idle",
        "avoid_hazard":"avoid_hazard",
        "explore_object":"explore_novel_object",
        "seek_dock":"dock_seek",
        "peer_status_ping":"peer_checkin",
    }
    return process_intent(mapping.get(action_name,"idle"), context)

def set_persona_state(data: dict):
    for k in ["energy","curiosity","affection","drama","caution"]:
        if data.get(k) is not None:
            setattr(state, k, clamp01(data[k]))
    if data.get("notes"):
        state.notes.extend(data["notes"])
        state.notes = state.notes[-20:]
    return get_persona_state()

def get_persona_state():
    return {
        "energy": state.energy,
        "curiosity": state.curiosity,
        "affection": state.affection,
        "drama": state.drama,
        "caution": state.caution,
        "mood": state.mood,
        "recent_behaviors": state.recent_behaviors[-10:],
        "notes": state.notes[-10:],
    }

def reset_state():
    state.energy=0.82; state.curiosity=0.86; state.affection=0.80; state.drama=0.42; state.caution=0.38; state.mood="bubbly"; state.recent_behaviors.clear(); state.notes.clear()
    return get_persona_state()
