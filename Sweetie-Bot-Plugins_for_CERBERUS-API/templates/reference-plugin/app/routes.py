from fastapi import APIRouter, HTTPException
from shared.sweetie_plugin_sdk.models import ExecuteRequest, ExecuteResponse
from shared.sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "plugin": "sweetie-plugin-reference", "version": "1.0.0"}


@router.get("/manifest")
def manifest():
    return load_manifest()


@router.get("/status")
def status():
    return {"status": "ok", "requests": 0}


@router.post("/execute")
def execute(req: ExecuteRequest):
    if req.action != "reference.ping":
        raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")
    return ExecuteResponse(
        request_id=req.request_id,
        plugin="sweetie-plugin-reference",
        action=req.action,
        version="1.0.0",
        result={"pong": True},
        state_patch={"reference": {"last_action": req.action}},
    ).model_dump()
