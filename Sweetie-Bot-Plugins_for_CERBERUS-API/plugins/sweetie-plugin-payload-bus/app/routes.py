from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import CapabilityRequest, PayloadDescriptor, PayloadIdRequest, RouteRequest
from app.services.registry import registry
from sweetie_plugin_sdk.manifest import load_manifest
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "plugin": settings.plugin_name,
        "version": settings.plugin_version,
    }

@router.get("/manifest")
def manifest():
    return load_manifest()

@router.get("/status")
def status():
    return registry.status()

@router.post("/execute")
def execute(req: ExecuteRequest):
    action = req.type.strip().lower()

    if action == "payload.register":
        descriptor = PayloadDescriptor(**req.payload)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"registered": registry.register(descriptor)},
        ).model_dump()

    if action == "payload.heartbeat":
        payload_id = PayloadIdRequest(**req.payload).id
        result = registry.heartbeat(payload_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Payload not found: {payload_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"heartbeat": result},
        ).model_dump()

    if action == "payload.unregister":
        payload_id = PayloadIdRequest(**req.payload).id
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"unregistered": registry.unregister(payload_id), "id": payload_id},
        ).model_dump()

    if action == "payload.get":
        payload_id = PayloadIdRequest(**req.payload).id
        result = registry.get(payload_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Payload not found: {payload_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"result": result},
        ).model_dump()

    if action == "payload.list":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"results": registry.list()},
        ).model_dump()

    if action == "payload.list_by_capability":
        capability = CapabilityRequest(**req.payload).capability
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"capability": capability, "results": registry.list_by_capability(capability)},
        ).model_dump()

    if action == "payload.route_request":
        model = RouteRequest(**req.payload)
        target = registry.route(model.capability, model.preferred_payload_id)
        if not target:
            raise HTTPException(status_code=404, detail=f"No payload registered for capability: {model.capability}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={
                "selected_target": target,
                "forwarding_envelope": {
                    "target_base_url": target["payload"]["base_url"],
                    "request": model.request,
                },
            },
        ).model_dump()

    if action == "payload.status":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=registry.status(),
        ).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
