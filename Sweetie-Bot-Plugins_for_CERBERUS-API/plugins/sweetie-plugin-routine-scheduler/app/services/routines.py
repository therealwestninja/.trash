from dataclasses import dataclass, field
import time

@dataclass
class Routine:
    name: str
    interval: float
    suggested_action: dict
    last_run: float = 0.0

@dataclass
class State:
    routines: dict = field(default_factory=dict)
state = State()

def add(name, interval, suggested_action):
    state.routines[name] = Routine(name, interval, suggested_action)
    return {"added": name, "interval": interval, "suggested_action": suggested_action}

def remove(name):
    state.routines.pop(name, None)
    return {"removed": name}

def list_all():
    return {k: v.__dict__ for k,v in state.routines.items()}

def tick():
    now = time.time()
    triggered = []
    for r in state.routines.values():
        if now - r.last_run >= r.interval:
            r.last_run = now
            triggered.append({"name": r.name, "suggested_action": r.suggested_action})
    return {"triggered": triggered}
