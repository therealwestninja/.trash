from dataclasses import dataclass, field
from math import hypot

def distance(a,b): return hypot(b["x"]-a["x"], b["y"]-a["y"])

@dataclass
class State:
    dock_name: str = "charging_dock"
    dock_position: dict | None = None
    mode: str = "idle"
    charging: bool = False
    last_plan: dict | None = None
    history: list[dict] = field(default_factory=list)
state = State()

def remember(entry):
    state.history.append(entry)
    state.history = state.history[-20:]

def set_dock(name, pos):
    state.dock_name = name
    state.dock_position = {"x": float(pos["x"]), "y": float(pos["y"])}
    remember({"event":"set_dock","dock_name":name})
    return {"dock_name": state.dock_name, "dock_position": state.dock_position}

def seek_dock(battery, current_position):
    if not state.dock_position:
        return {"should_dock":False,"reason":"dock_unknown","urgency":"none","suggested_action":None}
    urgency = "critical" if battery <= 0.10 else ("low" if battery <= 0.20 else "none")
    should_dock = urgency != "none"
    result = {"should_dock": should_dock, "reason": "battery_low" if should_dock else "battery_ok", "urgency": urgency, "dock_target": state.dock_position, "distance_to_dock_m": round(distance(current_position, state.dock_position),4)}
    if should_dock:
        state.mode = "seeking"
        result["suggested_action"] = {"type":"navigation.plan_to_point","payload":{"goal": state.dock_position, "purpose":"dock"}}
    else:
        result["suggested_action"] = None
    remember({"event":"seek_dock","urgency":urgency})
    return result

def plan_approach(current_position, dock_position=None):
    dock = dock_position or state.dock_position
    if not dock: return {"planned":False,"reason":"dock_unknown"}
    state.mode = "approaching"
    plan = {"planned":True,"dock_position": dock, "approach_point": dock, "suggested_action":{"type":"navigation.plan_to_point","payload":{"goal": dock, "purpose":"dock_approach"}}}
    state.last_plan = plan
    remember({"event":"plan_approach"})
    return plan

def align(current_position, dock_position=None):
    dock = dock_position or state.dock_position
    if not dock: return {"aligned":False,"reason":"dock_unknown"}
    d = distance(current_position, dock)
    aligned = d <= 0.20
    state.mode = "aligned" if aligned else "aligning"
    res = {"aligned": aligned, "distance_to_dock_m": round(d,4), "dock_position": dock, "suggested_action": None if aligned else {"type":"navigation.plan_to_point","payload":{"goal": dock, "purpose":"dock_align"}}}
    remember({"event":"align","aligned":aligned})
    return res

def begin_charge(confirmed_docked):
    if confirmed_docked:
        state.mode = "charging"; state.charging = True
        res = {"charging":True,"state":"charging"}
    else:
        res = {"charging":False,"state":state.mode,"reason":"dock_not_confirmed"}
    remember({"event":"begin_charge","charging":res["charging"]})
    return res

def get_state():
    return {"dock_name":state.dock_name,"dock_position":state.dock_position,"mode":state.mode,"charging":state.charging,"last_plan":state.last_plan,"history":state.history[-10:]}

def reset_state():
    state.dock_name="charging_dock"; state.dock_position=None; state.mode="idle"; state.charging=False; state.last_plan=None; state.history.clear()
    return get_state()
