from fastapi import APIRouter, HTTPException
from app.models import RoutineAddRequest
from app.services.routines import add, remove, list_all, tick, state
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
    if t == "routine.add":
        m = RoutineAddRequest(**req.payload); return PluginResponse(plugin="routine", action=req.type, data=add(m.name, m.interval, m.suggested_action)).model_dump()
    if t == "routine.remove":
        return PluginResponse(plugin="routine", action=req.type, data=remove(req.payload["name"])).model_dump()
    if t == "routine.list":
        return PluginResponse(plugin="routine", action=req.type, data={"routines": list_all()}).model_dump()
    if t == "routine.tick":
        return PluginResponse(plugin="routine", action=req.type, data=tick()).model_dump()
    if t == "routine.reset":
        state.routines.clear()
        return PluginResponse(plugin="routine", action=req.type, data={"reset":True}).model_dump()
    if t == "routine.status":
        return PluginResponse(plugin="routine", action=req.type, data={"count": len(state.routines), "routines": list_all()}).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
