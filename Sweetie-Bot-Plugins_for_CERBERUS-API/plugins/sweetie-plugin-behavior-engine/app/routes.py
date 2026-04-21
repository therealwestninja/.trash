from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import ProcessIntentRequest, GenerateStyleRequest, SetPersonaStateRequest
from app.services.behavior import process_intent, generate_style, set_persona_state, get_persona_state, reset_state
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
    if t == "behavior.process_intent":
        m = ProcessIntentRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=process_intent(m.intent, m.context)).model_dump()
    if t == "behavior.generate_style":
        m = GenerateStyleRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=generate_style(m.action_name, m.context)).model_dump()
    if t == "behavior.set_persona_state":
        m = SetPersonaStateRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": set_persona_state(m.model_dump())}).model_dump()
    if t == "behavior.get_persona_state":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": get_persona_state()}).model_dump()
    if t == "behavior.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": reset_state()}).model_dump()
    if t == "behavior.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=get_persona_state()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
