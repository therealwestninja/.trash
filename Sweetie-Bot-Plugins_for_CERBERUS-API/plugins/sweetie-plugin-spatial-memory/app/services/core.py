from math import hypot
from dataclasses import dataclass, field

@dataclass
class State:
    position: dict = field(default_factory=lambda: {"x":0.0,"y":0.0})
    locations: dict = field(default_factory=dict)

state = State()

def remember(name, pos, confidence, metadata):
    state.locations[name] = {"position": pos, "confidence": confidence, "metadata": metadata}
    return {"stored": name, **state.locations[name]}

def get_location(name):
    return state.locations.get(name)

def list_locations():
    return state.locations

def update_position(pos):
    state.position = {"x": float(pos["x"]), "y": float(pos["y"])}
    return {"position": state.position}

def get_nearby(radius):
    results = {}
    for name, item in state.locations.items():
        pos = item["position"]
        d = hypot(pos["x"]-state.position["x"], pos["y"]-state.position["y"])
        if d <= radius:
            results[name] = {**item, "distance": round(d,4)}
    return results

def export_knowledge():
    out = []
    for name, item in state.locations.items():
        out.append({"name": name, "position": item["position"], "confidence": item["confidence"], "metadata": item["metadata"]})
    return out
