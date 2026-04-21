from fastapi import APIRouter, HTTPException
from app.models import SetPositionRequest, PlanToPointRequest, PlanToLocationRequest, FollowRouteRequest
from app.services.navigation import set_position, plan_to_point, plan_to_location, follow_route, cancel_route, get_route, status
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()
@router.get("/health")
def health(): return {"status":"ok"}
@router.get("/manifest")
def manifest(): return load_manifest()
@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type.strip().lower()
    if t == "navigation.set_position":
        m = SetPositionRequest(**req.payload); return PluginResponse(plugin="navigation", action=req.type, data=set_position(m.position.model_dump())).model_dump()
    if t == "navigation.plan_to_point":
        m = PlanToPointRequest(**req.payload); return PluginResponse(plugin="navigation", action=req.type, data={"route": plan_to_point(m.goal.model_dump(), m.purpose)}).model_dump()
    if t == "navigation.plan_to_location":
        m = PlanToLocationRequest(**req.payload); route = plan_to_location(m.name, m.locations, m.purpose)
        if not route: raise HTTPException(status_code=404, detail="location_not_found")
        return PluginResponse(plugin="navigation", action=req.type, data={"route": route}).model_dump()
    if t == "navigation.follow_route":
        m = FollowRouteRequest(**req.payload); route = follow_route(m.route_id)
        if not route: raise HTTPException(status_code=404, detail="route_not_found")
        return PluginResponse(plugin="navigation", action=req.type, data={"route": route}).model_dump()
    if t == "navigation.cancel_route":
        return PluginResponse(plugin="navigation", action=req.type, data=cancel_route()).model_dump()
    if t == "navigation.get_route":
        return PluginResponse(plugin="navigation", action=req.type, data={"route": get_route()}).model_dump()
    if t == "navigation.status":
        return PluginResponse(plugin="navigation", action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
