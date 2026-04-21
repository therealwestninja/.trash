from fastapi import APIRouter, HTTPException
from app.models import SetDockRequest, SeekDockRequest, PlanApproachRequest, AlignRequest, BeginChargeRequest
from app.services.docking import set_dock, seek_dock, plan_approach, align, begin_charge, get_state, reset_state
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
    if t == "docking.set_dock":
        m = SetDockRequest(**req.payload); return PluginResponse(plugin="docking", action=req.type, data=set_dock(m.dock_name, m.position.model_dump())).model_dump()
    if t == "docking.seek_dock":
        m = SeekDockRequest(**req.payload); return PluginResponse(plugin="docking", action=req.type, data=seek_dock(m.battery, m.current_position.model_dump())).model_dump()
    if t == "docking.plan_approach":
        m = PlanApproachRequest(**req.payload); dock = m.dock_position.model_dump() if m.dock_position else None
        return PluginResponse(plugin="docking", action=req.type, data=plan_approach(m.current_position.model_dump(), dock)).model_dump()
    if t == "docking.align":
        m = AlignRequest(**req.payload); dock = m.dock_position.model_dump() if m.dock_position else None
        return PluginResponse(plugin="docking", action=req.type, data=align(m.current_position.model_dump(), dock)).model_dump()
    if t == "docking.begin_charge":
        m = BeginChargeRequest(**req.payload); return PluginResponse(plugin="docking", action=req.type, data=begin_charge(m.confirmed_docked)).model_dump()
    if t == "docking.get_state":
        return PluginResponse(plugin="docking", action=req.type, data=get_state()).model_dump()
    if t == "docking.reset":
        return PluginResponse(plugin="docking", action=req.type, data=reset_state()).model_dump()
    if t == "docking.status":
        return PluginResponse(plugin="docking", action=req.type, data=get_state()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
