from dataclasses import dataclass, field
from app.config import settings

@dataclass
class State:
    estop_active: bool = False
    policy: dict = field(default_factory=lambda:{
        "max_speed_mps": settings.max_speed_mps,
        "public_min_distance_m": settings.public_min_distance_m,
        "supporting_min_distance_m": settings.supporting_min_distance_m,
        "best_friend_min_distance_m": settings.best_friend_min_distance_m,
        "low_battery_threshold": settings.low_battery_threshold,
    })
    last_context: dict = field(default_factory=dict)
    recent_decisions: list[dict] = field(default_factory=list)

state = State()

def get_policy():
    return {"estop_active": state.estop_active, **state.policy}

def set_policy(data: dict):
    for k,v in data.items():
        if v is not None and k in state.policy:
            state.policy[k] = v
    return get_policy()

def report_context(ctx: dict):
    state.last_context = dict(ctx)
    return {"last_context": state.last_context}

def estop():
    state.estop_active = True
    return {"estop_active": True}

def clear_estop():
    state.estop_active = False
    return {"estop_active": False}

def _distance_for_tier(tier: str) -> float:
    if tier == "best_friend":
        return state.policy["best_friend_min_distance_m"]
    if tier == "supporting":
        return state.policy["supporting_min_distance_m"]
    return state.policy["public_min_distance_m"]

def evaluate_action(action: dict, context: dict):
    decision = "allow"
    reasons = []
    flags = []
    normalized = {"type": action.get("type",""), "payload": dict(action.get("payload", {}))}
    payload = normalized["payload"]

    if state.estop_active:
        decision = "block"; reasons.append("estop_active"); flags.append("estop")

    if context.get("autonomy_mode") == "safe_stop" and normalized["type"] not in {"safety.estop","docking.get_state"}:
        decision = "block"; reasons.append("autonomy_safe_stop"); flags.append("autonomy")

    speed = float(payload.get("speed_mps", 0.0) or 0.0)
    if speed > state.policy["max_speed_mps"]:
        decision = "warn" if decision == "allow" else decision
        reasons.append("speed_limited"); flags.append("speed")
        payload["speed_mps"] = state.policy["max_speed_mps"]

    battery = float(context.get("battery", 1.0) or 1.0)
    if battery <= state.policy["low_battery_threshold"] and normalized["type"] in {"runtime.follow_object","robot.command","navigation.follow_route"}:
        decision = "warn" if decision == "allow" else decision
        reasons.append("low_battery")

    tier = context.get("relationship_tier", "public")
    nearest_human = context.get("nearest_human_distance_m")
    if nearest_human is not None:
        required = _distance_for_tier(tier)
        nearest_human = float(nearest_human)
        if nearest_human < required:
            decision = "warn" if decision == "allow" else decision
            reasons.append(f"distance_adjusted_for_{tier}")
            payload["target_distance_m"] = max(float(payload.get("target_distance_m", nearest_human)), required)
            flags.append("distance")

    if normalized["type"] == "crusader.send_message":
        # allowed but screened
        if context.get("safety_blocked"):
            decision = "warn" if decision == "allow" else decision
            reasons.append("squad_message_during_safety_event")

    result = {"decision":decision,"reasons":reasons,"safety_flags":flags,"normalized_action":normalized,"policy":get_policy()}
    state.recent_decisions.append(result)
    state.recent_decisions = state.recent_decisions[-20:]
    return result

def status():
    return {"policy": get_policy(), "last_context": state.last_context, "recent_decisions": state.recent_decisions[-10:]}
