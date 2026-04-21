from math import hypot
from app.state import state

def remember(name, pos):
    state.locations[name] = pos
    return {"stored": name, "position": pos}

def get_location(name):
    return state.locations.get(name)

def list_locations():
    return state.locations

def update_position(pos):
    state.position = pos
    return {"position": pos}

def get_nearby(radius):
    results = {}
    for name, pos in state.locations.items():
        d = hypot(pos["x"]-state.position["x"], pos["y"]-state.position["y"])
        if d <= radius:
            results[name] = {"position": pos, "distance": round(d,3)}
    return results
