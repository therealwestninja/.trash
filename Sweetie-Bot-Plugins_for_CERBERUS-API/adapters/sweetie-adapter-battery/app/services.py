from dataclasses import dataclass

@dataclass
class State:
    level: float = 1.0
    charging: bool = False

state = State()

def set_level(level: float):
    state.level = max(0.0, min(1.0, float(level)))
    return get_state()

def set_charging(charging: bool):
    state.charging = bool(charging)
    return get_state()

def get_state():
    return {"battery": state.level, "charging": state.charging}
