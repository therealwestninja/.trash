import time
from state import state, Routine

def add(name, interval):
    state.routines[name] = Routine(name, interval)
    return {"added": name, "interval": interval}

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
            triggered.append(r.name)
    return {"triggered": triggered}
