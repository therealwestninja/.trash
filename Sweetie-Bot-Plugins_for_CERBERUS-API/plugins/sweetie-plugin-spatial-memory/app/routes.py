from fastapi import APIRouter, HTTPException
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest
from app.models import RememberLocationRequest, UpdatePositionRequest, GetNearbyRequest
from app.services.core import remember, get_location, list_locations, update_position, get_nearby, export_knowledge, state

router = APIRouter()

@router.get("/health")
def health(): return {"status":"ok"}
@router.get("/manifest")
def manifest(): return load_manifest()

@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type.strip().lower()
    if t == "spatial.remember_location":
        m = RememberLocationRequest(**req.payload)
        return PluginResponse(plugin="spatial", action=req.type, data=remember(m.name, m.position, m.confidence, m.metadata)).model_dump()
    if t == "spatial.get_location":
        return PluginResponse(plugin="spatial", action=req.type, data={"location": get_location(req.payload["name"])}).model_dump()
    if t == "spatial.list_locations":
        return PluginResponse(plugin="spatial", action=req.type, data={"locations": list_locations()}).model_dump()
    if t == "spatial.update_position":
        m = UpdatePositionRequest(**req.payload)
        return PluginResponse(plugin="spatial", action=req.type, data=update_position(m.position)).model_dump()
    if t == "spatial.get_nearby":
        m = GetNearbyRequest(**req.payload)
        return PluginResponse(plugin="spatial", action=req.type, data={"nearby": get_nearby(m.radius)}).model_dump()
    if t == "spatial.export_knowledge":
        return PluginResponse(plugin="spatial", action=req.type, data={"locations": export_knowledge()}).model_dump()
    if t == "spatial.reset":
        state.locations.clear()
        return PluginResponse(plugin="spatial", action=req.type, data={"reset":True}).model_dump()
    if t == "spatial.status":
        return PluginResponse(plugin="spatial", action=req.type, data={"state":{"position": state.position, "location_count": len(state.locations)}}).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
