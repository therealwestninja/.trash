from dataclasses import dataclass, field
from datetime import datetime, UTC
from math import hypot
import uuid

def now_iso(): return datetime.now(UTC).isoformat()

@dataclass
class State:
    position: dict = field(default_factory=lambda: {"x":0.0,"y":0.0})
    active_route: dict | None = None
    recent_routes: list[dict] = field(default_factory=list)
state = State()

def distance(a,b): return hypot(b["x"]-a["x"], b["y"]-a["y"])

def interpolate(start, goal, step=0.5):
    total = distance(start, goal)
    if total == 0: return [dict(start)]
    steps = max(1, int(total / step))
    pts = []
    for i in range(steps+1):
        t = i/steps
        pts.append({"x": round(start["x"]+(goal["x"]-start["x"])*t,4), "y": round(start["y"]+(goal["y"]-start["y"])*t,4)})
    return pts

def set_position(pos):
    state.position = {"x": float(pos["x"]), "y": float(pos["y"])}
    return {"position": state.position}

def _store(goal, points, source, purpose):
    route = {"route_id": str(uuid.uuid4()), "created_at": now_iso(), "source": source, "purpose": purpose, "start": dict(state.position), "goal": goal, "waypoints": points, "status": "planned"}
    state.active_route = route
    state.recent_routes.append(route)
    state.recent_routes = state.recent_routes[-20:]
    return route

def plan_to_point(goal, purpose):
    return _store({"x": float(goal["x"]), "y": float(goal["y"])}, interpolate(state.position, goal), "point", purpose)

def plan_to_location(name, locations, purpose):
    loc = locations.get(name)
    if not loc: return None
    route = _store({"x": float(loc["x"]), "y": float(loc["y"])}, interpolate(state.position, loc), f"location:{name}", purpose)
    route["location_name"] = name
    return route

def follow_route(route_id):
    if not state.active_route or state.active_route["route_id"] != route_id: return None
    state.active_route["status"] = "following"
    state.position = dict(state.active_route["goal"])
    state.active_route["status"] = "completed"
    return state.active_route

def cancel_route():
    rid = state.active_route["route_id"] if state.active_route else None
    if state.active_route: state.active_route["status"] = "cancelled"
    state.active_route = None
    return {"cancelled": bool(rid), "route_id": rid}

def get_route(): return state.active_route
def status(): return {"position": state.position, "active_route": state.active_route, "recent_routes": state.recent_routes[-10:]}
