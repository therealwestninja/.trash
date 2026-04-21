from fastapi import APIRouter, HTTPException
from app.models import ProfileRequest, GaitRequest, GetGaitRequest, AdaptCommandRequest, PreviewSequenceRequest
from app.services.library import list_profiles, list_gaits, get_gait, set_active, get_active, adapt_command, preview_sequence
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
    try:
        if t == "gait.list_profiles":
            return PluginResponse(plugin="gait-library", action=req.type, data={"profiles": list_profiles()}).model_dump()
        if t == "gait.list_gaits":
            m = ProfileRequest(**req.payload); return PluginResponse(plugin="gait-library", action=req.type, data={"profile": m.profile, "gaits": list_gaits(m.profile)}).model_dump()
        if t == "gait.get_gait":
            m = GetGaitRequest(**req.payload); prof = m.profile or get_active()["active_profile"]; g = get_gait(prof, m.gait)
            if not g: raise HTTPException(status_code=404, detail="gait_not_found")
            return PluginResponse(plugin="gait-library", action=req.type, data={"profile": prof, "gait_name": m.gait, "gait": g}).model_dump()
        if t == "gait.set_active":
            m = GaitRequest(**req.payload); return PluginResponse(plugin="gait-library", action=req.type, data=set_active(m.profile, m.gait)).model_dump()
        if t == "gait.get_active":
            return PluginResponse(plugin="gait-library", action=req.type, data=get_active()).model_dump()
        if t == "gait.adapt_command":
            m = AdaptCommandRequest(**req.payload); return PluginResponse(plugin="gait-library", action=req.type, data=adapt_command(m.command, m.profile, m.gait, m.autonomy_mode, m.movement_style)).model_dump()
        if t == "gait.preview_sequence":
            m = PreviewSequenceRequest(**req.payload); return PluginResponse(plugin="gait-library", action=req.type, data=preview_sequence(m.profile, m.gait, m.seconds)).model_dump()
        if t == "gait.status":
            return PluginResponse(plugin="gait-library", action=req.type, data=get_active()).model_dump()
    except KeyError:
        raise HTTPException(status_code=400, detail="unknown_gait")
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
