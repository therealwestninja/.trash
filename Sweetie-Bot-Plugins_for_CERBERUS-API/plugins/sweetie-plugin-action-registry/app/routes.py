from fastapi import APIRouter, HTTPException
from app.models import ActionRegistration, ActionNameRequest, DispatchRequest, SetPolicyRequest
from app.services.registry import register_action, unregister_action, list_actions, get_action, dispatch, set_policy, seed_defaults, status
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
    if t == "action.register":
        m = ActionRegistration(**req.payload); return PluginResponse(plugin="action-registry", action=req.type, data={"registered": register_action(m)}).model_dump()
    if t == "action.unregister":
        m = ActionNameRequest(**req.payload); return PluginResponse(plugin="action-registry", action=req.type, data=unregister_action(m.action_name)).model_dump()
    if t == "action.list":
        return PluginResponse(plugin="action-registry", action=req.type, data={"results": list_actions()}).model_dump()
    if t == "action.get":
        m = ActionNameRequest(**req.payload); res = get_action(m.action_name)
        if not res: raise HTTPException(status_code=404, detail="action_not_found")
        return PluginResponse(plugin="action-registry", action=req.type, data={"result": res}).model_dump()
    if t == "action.dispatch":
        m = DispatchRequest(**req.payload); res = dispatch(m.action_name, m.payload_override)
        if not res: raise HTTPException(status_code=404, detail="action_not_found")
        return PluginResponse(plugin="action-registry", action=req.type, data=res).model_dump()
    if t == "action.set_policy":
        m = SetPolicyRequest(**req.payload); res = set_policy(m.action_name, m.policy)
        if not res: raise HTTPException(status_code=404, detail="action_not_found")
        return PluginResponse(plugin="action-registry", action=req.type, data={"updated": res}).model_dump()
    if t == "action.seed_defaults":
        return PluginResponse(plugin="action-registry", action=req.type, data=seed_defaults()).model_dump()
    if t == "action.status":
        return PluginResponse(plugin="action-registry", action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
