from fastapi import APIRouter, HTTPException
from app.models import ReportContextRequest, TransitionRequest, SetPolicyRequest
from app.services.supervisor import report_context, evaluate_mode, choose_goal_from_context, approve_transition, get_state, set_policy, reset, status
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
    if t == "autonomy.report_context":
        m = ReportContextRequest(**req.payload); return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=report_context(m.model_dump())).model_dump()
    if t == "autonomy.evaluate_mode":
        m = ReportContextRequest(**req.payload); return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=evaluate_mode(m.model_dump())).model_dump()
    if t == "autonomy.choose_goal":
        ctx = req.payload.get("context", {}); return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=choose_goal_from_context(ctx)).model_dump()
    if t == "autonomy.approve_transition":
        m = TransitionRequest(**req.payload); return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=approve_transition(m.from_mode,m.to_mode,m.reason)).model_dump()
    if t == "autonomy.get_state":
        return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=get_state()).model_dump()
    if t == "autonomy.set_policy":
        m = SetPolicyRequest(**req.payload); return PluginResponse(plugin="autonomy-supervisor", action=req.type, data={"policy": set_policy(m.model_dump())}).model_dump()
    if t == "autonomy.reset":
        return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=reset()).model_dump()
    if t == "autonomy.status":
        return PluginResponse(plugin="autonomy-supervisor", action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
