from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict

import httpx

from app.config import settings
from app.models import PatrolMissionRequest, RegisterRoutesRequest

@dataclass
class OrchestratorState:
    routes: Dict[str, str] = field(default_factory=lambda: {
        "registry": settings.registry_url,
        "world_model": settings.world_model_url,
        "nav": settings.nav_url,
        "mission": settings.mission_url,
        "sim": settings.sim_url,
    })
    last_results: list[dict] = field(default_factory=list)

state = OrchestratorState()

def register_routes(model: RegisterRoutesRequest) -> dict:
    updates = {}
    for key in ["registry_url", "world_model_url", "nav_url", "mission_url", "sim_url"]:
        value = getattr(model, key)
        if value:
            route_key = key.replace("_url", "")
            state.routes[route_key] = value
            updates[route_key] = value
    return {"updated_routes": updates, "routes": state.routes}

def build_follow_object_goal(obj: dict, standoff_m: float) -> dict:
    pos = obj["object"]["position"]
    target_x = pos["x"] - standoff_m
    target_y = pos["y"]
    return {
        "type": "nav.goal",
        "payload": {
            "x": round(target_x, 4),
            "y": round(target_y, 4),
            "yaw": 0.0,
            "frame": obj["object"].get("frame", "map"),
        },
    }

def build_patrol_mission(model: PatrolMissionRequest) -> dict:
    nodes = []
    for wp in model.waypoints:
        nodes.append({"action": "nav.goal", "payload": {"x": wp.x, "y": wp.y}})
    if model.loop and model.waypoints:
        first = model.waypoints[0]
        nodes.append({"action": "nav.goal", "payload": {"x": first.x, "y": first.y}})
    return {
        "type": "sequence",
        "nodes": nodes,
    }

async def call_execute(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{url.rstrip('/')}/execute", json=payload)
        response.raise_for_status()
        return response.json()

def remember(result: dict):
    state.last_results.append(result)
    state.last_results = state.last_results[-20:]
