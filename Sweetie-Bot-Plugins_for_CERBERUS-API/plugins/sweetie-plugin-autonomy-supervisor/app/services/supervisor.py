from dataclasses import dataclass, field

@dataclass
class State:
    mode: str = "idle"
    goal: str | None = None
    last_context: dict = field(default_factory=dict)
    policy: dict = field(default_factory=lambda: {
        "low_battery": 0.20,
        "critical_battery": 0.10,
        "idle_timeout_sec": 300,
        "social_window_sec": 90,
        "exploration_enabled": True,
    })
    history: list[dict] = field(default_factory=list)
state = State()

def remember(entry): state.history.append(entry); state.history = state.history[-40:]

def report_context(ctx):
    state.last_context = dict(ctx)
    mode = evaluate_mode(ctx)["mode"]
    state.mode = mode
    goal = choose_goal_from_context(ctx, mode)["goal"]
    state.goal = goal
    res = {"mode": state.mode, "goal": state.goal, "context": state.last_context}
    remember({"event":"report_context", **res})
    return res

def evaluate_mode(ctx):
    battery = float(ctx.get("battery",1.0))
    if ctx.get("safety_blocked"):
        res = {"mode":"safe_stop","reason":"safety_blocked"}
    elif ctx.get("charging"):
        res = {"mode":"charging","reason":"currently_charging"}
    elif battery <= state.policy["critical_battery"] and ctx.get("dock_known"):
        res = {"mode":"dock_urgent","reason":"critical_battery"}
    elif battery <= state.policy["low_battery"] and ctx.get("dock_known"):
        res = {"mode":"dock_seek","reason":"low_battery"}
    elif ctx.get("best_friend_visible") or ctx.get("operator_visible"):
        res = {"mode":"follow_operator","reason":"best_friend_visible"}
    elif ctx.get("supporting_visible") or ctx.get("social_target_visible"):
        res = {"mode":"social","reason":"social_target_visible"}
    elif ctx.get("peer_online") and not ctx.get("public_present"):
        res = {"mode":"team_sync","reason":"peer_online"}
    elif ctx.get("routine_triggered"):
        res = {"mode":"routine","reason":"routine_triggered"}
    elif state.policy["exploration_enabled"]:
        res = {"mode":"explore","reason":"exploration_enabled"}
    else:
        res = {"mode":"idle","reason":"default_idle"}
    remember({"event":"evaluate_mode", **res})
    return res

def choose_goal_from_context(ctx, mode=None):
    mode = mode or state.mode
    if mode == "safe_stop":
        res = {"goal":"halt_and_wait","suggested_action":{"type":"safety.estop","payload":{}},"mode":mode}
    elif mode in {"dock_seek","dock_urgent"}:
        res = {"goal":"reach_charging_dock","suggested_action":{"type":"docking.seek_dock","payload":{"battery": ctx.get("battery",1.0),"current_position": ctx.get("current_position", {"x":0.0,"y":0.0})}},"mode":mode}
    elif mode == "charging":
        res = {"goal":"remain_charging","suggested_action":{"type":"docking.get_state","payload":{}},"mode":mode}
    elif mode == "follow_operator":
        res = {"goal":"stay_with_best_friend","suggested_action":{"type":"action.dispatch","payload":{"action_name":"follow_operator","payload_override":{}}},"mode":mode}
    elif mode == "social":
        res = {"goal":"engage_social_target","suggested_action":{"type":"interaction.process_event","payload":{"event":{"topic":"vision.person_detected","payload":{"tags":[]}}}},"mode":mode}
    elif mode == "team_sync":
        res = {"goal":"coordinate_with_crusaders","suggested_action":{"type":"action.dispatch","payload":{"action_name":"peer_status_ping","payload_override":{}}},"mode":mode}
    elif mode == "routine":
        routine = ctx.get("routine_triggered",[None])[0]
        res = {"goal":f"execute_routine:{routine or 'routine'}","suggested_action":{"type":"routine.tick","payload":{}},"mode":mode}
    elif mode == "explore":
        res = {"goal":"curious_safe_exploration","suggested_action":{"type":"action.dispatch","payload":{"action_name":"idle_scan","payload_override":{}}},"mode":mode}
    else:
        res = {"goal":"idle_observe","suggested_action":{"type":"action.dispatch","payload":{"action_name":"idle_scan","payload_override":{}}},"mode":mode}
    remember({"event":"choose_goal", **res})
    return res

def approve_transition(from_mode, to_mode, reason):
    blocked = False; block_reason = None
    if from_mode == "charging" and to_mode not in {"safe_stop","charging"}:
        blocked = True; block_reason = "cannot_leave_charging_without_explicit_release"
    if state.last_context.get("safety_blocked") and to_mode != "safe_stop":
        blocked = True; block_reason = "safety_blocked"
    if state.last_context.get("battery",1.0) <= state.policy["critical_battery"] and to_mode not in {"dock_urgent","charging","safe_stop"}:
        blocked = True; block_reason = "critical_battery_priority"
    res = {"approved": not blocked, "from_mode": from_mode, "to_mode": to_mode, "reason": reason, "block_reason": block_reason}
    if res["approved"]: state.mode = to_mode
    remember({"event":"approve_transition", **res})
    return res

def get_state():
    return {"mode": state.mode, "goal": state.goal, "last_context": state.last_context, "policy": state.policy, "recent_history": state.history[-10:]}

def set_policy(data):
    for k in ["low_battery","critical_battery"]:
        if data.get(k) is not None: state.policy[k] = max(0.0, min(1.0, float(data[k])))
    for k in ["idle_timeout_sec","social_window_sec"]:
        if data.get(k) is not None: state.policy[k] = max(1, int(data[k]))
    if data.get("exploration_enabled") is not None: state.policy["exploration_enabled"] = bool(data["exploration_enabled"])
    remember({"event":"set_policy","policy": state.policy})
    return state.policy

def reset():
    state.mode="idle"; state.goal=None; state.last_context={}; state.policy={"low_battery":0.20,"critical_battery":0.10,"idle_timeout_sec":300,"social_window_sec":90,"exploration_enabled":True}; state.history.clear()
    return get_state()

def status(): return {**get_state(), "history_count": len(state.history)}
