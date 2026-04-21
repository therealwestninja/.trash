from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import EvaluateActionRequest, SetPolicyRequest, ReportContextRequest
from app.services.safety import evaluate_action, set_policy, get_policy, report_context, estop, clear_estop, status
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
    if t == "safety.evaluate_action":
        m = EvaluateActionRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=evaluate_action(m.action, m.context)).model_dump()
    if t == "safety.set_policy":
        m = SetPolicyRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"policy": set_policy(m.model_dump())}).model_dump()
    if t == "safety.get_policy":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"policy": get_policy()}).model_dump()
    if t == "safety.report_context":
        m = ReportContextRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=report_context(m.context)).model_dump()
    if t == "safety.estop":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=estop()).model_dump()
    if t == "safety.clear_estop":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=clear_estop()).model_dump()
    if t == "safety.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
