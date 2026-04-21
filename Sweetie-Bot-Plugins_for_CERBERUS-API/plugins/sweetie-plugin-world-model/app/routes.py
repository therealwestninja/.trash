from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import DeleteObjectRequest, GetObjectRequest, ObservationBatch, QueryNearRequest, WorldObject
from app.services.store import store
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
    return store.status()

@router.post("/execute")
def execute(req: ExecuteRequest):
    action = req.type.strip().lower()

    if action == "world.upsert_object":
        obj = WorldObject(**req.payload)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"stored": store.upsert(obj)},
        ).model_dump()

    if action == "world.observe":
        batch = ObservationBatch(**req.payload)
        stored = [store.upsert(obj) for obj in batch.objects]
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"source": batch.source, "stored_count": len(stored), "stored": stored},
        ).model_dump()

    if action == "world.get_object":
        model = GetObjectRequest(**req.payload)
        found = store.get(model.id)
        if not found:
            raise HTTPException(status_code=404, detail=f"Object not found: {model.id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"result": found},
        ).model_dump()

    if action == "world.list_objects":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"results": store.list()},
        ).model_dump()

    if action == "world.delete_object":
        model = DeleteObjectRequest(**req.payload)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"deleted": store.delete(model.id), "id": model.id},
        ).model_dump()

    if action == "world.clear":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"cleared_count": store.clear()},
        ).model_dump()

    if action == "world.query_near":
        model = QueryNearRequest(**req.payload)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"results": store.query_near(model)},
        ).model_dump()

    if action == "world.status":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=store.status(),
        ).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
