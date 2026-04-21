from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import FollowWaypointsRequest, NavGoalRequest, NavPreviewRequest, RecoveryRequest, Point2D
from app.services.planner import PlannerState, build_recovery
from app.services.ros2_forwarder import maybe_forward
from sweetie_plugin_sdk.manifest import load_manifest
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse

router = APIRouter()
planner = PlannerState()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "plugin": settings.plugin_name,
        "version": settings.plugin_version,
        "forward_to_ros2": settings.forward_to_ros2,
    }

@router.get("/manifest")
def manifest():
    return load_manifest()

@router.get("/status")
def status():
    return {
        "active_plan": planner.active_plan.model_dump() if planner.active_plan else None,
        "last_route_points": [p.model_dump() for p in planner.last_route_points],
    }

@router.post("/execute")
async def execute(req: ExecuteRequest):
    action = req.type.strip().lower()

    if action == "nav.goal":
        model = NavGoalRequest(**req.payload)
        waypoints = [Point2D(x=0.0, y=0.0), Point2D(x=model.x, y=model.y)]
        plan = planner.create_plan(frame=model.frame, waypoints=waypoints, speed_mps=settings.max_speed_mps, notes=[
            f"behavior={model.behavior or 'default'}",
            f"tolerance_m={model.tolerance_m}",
        ])
        forwarded = await maybe_forward("nav.goal", model.model_dump())
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "plan": plan.model_dump(),
                "goal": model.model_dump(),
                "forwarded": forwarded,
            },
        ).model_dump()

    if action == "nav.preview_route":
        model = NavPreviewRequest(**req.payload)
        plan = planner.create_plan(frame=model.frame, waypoints=[model.start, model.goal], speed_mps=settings.max_speed_mps, notes=[
            "preview_only=true",
        ])
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "route_preview": [p.model_dump() for p in plan.route_points],
                "frame": model.frame,
                "estimated_points": len(plan.route_points),
            },
        ).model_dump()

    if action == "nav.follow_waypoints":
        model = FollowWaypointsRequest(**req.payload)
        if not model.waypoints:
            raise HTTPException(status_code=400, detail="waypoints cannot be empty")
        route_points = model.waypoints[:]
        if model.loop and len(route_points) > 1:
            route_points = route_points + [route_points[0]]
        speed = model.speed_mps or settings.max_speed_mps
        plan = planner.create_plan(frame=model.frame, waypoints=route_points, speed_mps=speed, notes=[
            f"loop={model.loop}",
            f"speed_mps={speed}",
        ])
        forwarded = await maybe_forward("nav.follow_waypoints", model.model_dump())
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "plan": plan.model_dump(),
                "waypoint_count": len(model.waypoints),
                "forwarded": forwarded,
            },
        ).model_dump()

    if action == "nav.recovery":
        model = RecoveryRequest(**req.payload)
        recovery = build_recovery(model.issue)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "issue": model.issue,
                "context": model.context,
                "recovery": recovery,
            },
        ).model_dump()

    if action == "nav.cancel":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=planner.cancel(),
        ).model_dump()

    if action == "nav.status":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "active_plan": planner.active_plan.model_dump() if planner.active_plan else None,
                "last_route_points": [p.model_dump() for p in planner.last_route_points],
            },
        ).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
