from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Iterable

from app.models import ActivePlan, Point2D

def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def interpolate_segment(start: Point2D, goal: Point2D, steps: int = 8) -> list[Point2D]:
    steps = max(2, steps)
    points: list[Point2D] = []
    for i in range(steps + 1):
        t = i / steps
        points.append(Point2D(x=round(_lerp(start.x, goal.x, t), 4), y=round(_lerp(start.y, goal.y, t), 4)))
    return points

def distance(a: Point2D, b: Point2D) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)

def stitch_route(points: list[Point2D]) -> list[Point2D]:
    if len(points) < 2:
        return points[:]
    route: list[Point2D] = []
    for idx in range(len(points) - 1):
        segment = interpolate_segment(points[idx], points[idx + 1], steps=8)
        if route:
            segment = segment[1:]
        route.extend(segment)
    return route

def estimate_duration_seconds(route: Iterable[Point2D], speed_mps: float) -> float:
    route = list(route)
    if len(route) < 2 or speed_mps <= 0:
        return 0.0
    total = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
    return round(total / speed_mps, 2)

@dataclass
class PlannerState:
    active_plan: ActivePlan | None = None
    last_route_points: list[Point2D] = field(default_factory=list)

    def create_plan(self, frame: str, waypoints: list[Point2D], speed_mps: float, notes: list[str] | None = None) -> ActivePlan:
        route = stitch_route(waypoints)
        plan = ActivePlan(
            plan_id=str(uuid.uuid4()),
            frame=frame,
            status="planned",
            waypoints=waypoints,
            route_points=route,
            notes=list(notes or []),
        )
        plan.notes.append(f"estimated_duration_seconds={estimate_duration_seconds(route, speed_mps)}")
        self.active_plan = plan
        self.last_route_points = route
        return plan

    def cancel(self) -> dict:
        previous = self.active_plan.plan_id if self.active_plan else None
        self.active_plan = None
        return {"cancelled": bool(previous), "plan_id": previous}

def build_recovery(issue: str) -> dict:
    normalized = issue.strip().lower()
    mapping = {
        "blocked_front": {
            "recommended_actions": ["stop", "micro_backup", "turn_left_15deg", "replan"],
            "severity": "medium",
        },
        "lost_localization": {
            "recommended_actions": ["stop", "switch_to_safe_stance", "relocalize", "retry_goal"],
            "severity": "high",
        },
        "narrow_passage": {
            "recommended_actions": ["slow_mode", "center_body", "reduce_turn_rate", "continue_with_caution"],
            "severity": "medium",
        },
        "slip_detected": {
            "recommended_actions": ["stop", "stance_widen", "terrain_check", "retry_low_speed"],
            "severity": "high",
        },
    }
    return mapping.get(
        normalized,
        {"recommended_actions": ["stop", "assess", "replan"], "severity": "unknown"},
    )
