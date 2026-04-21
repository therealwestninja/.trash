from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import RecordOutcomeRequest, AdjustTraitsRequest
from app.services.learning import record_outcome, adjust_traits, get_profile, get_history, reset, status
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()
@router.get("/health")
def health(): return {"status":"ok","plugin":settings.plugin_name,"version":settings.plugin_version}
@router.get("/manifest")
def manifest(): return load_manifest()
@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type.strip().lower()
    if t == "learning.record_outcome":
        m = RecordOutcomeRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"entry": record_outcome(m.behavior,m.outcome,m.reward,m.tags,m.notes,m.relationship_tier,m.autonomy_mode)}).model_dump()
    if t == "learning.adjust_traits":
        m = AdjustTraitsRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"profile": adjust_traits(m.model_dump())}).model_dump()
    if t == "learning.get_profile":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"profile": get_profile()}).model_dump()
    if t == "learning.get_history":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"history": get_history(int(req.payload.get("limit",25)))}).model_dump()
    if t == "learning.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"profile": reset()}).model_dump()
    if t == "learning.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
