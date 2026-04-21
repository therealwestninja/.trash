from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import DatasetExportRequest, EpisodeEndRequest, EpisodeStartRequest, ReplayCreateRequest, ReplayGetRequest, StepRequest
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

    if action == "sim.episode_start":
        model = EpisodeStartRequest(**req.payload)
        episode = store.episode_start(model.episode_name, model.scenario, model.metadata)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"episode": episode},
        ).model_dump()

    if action == "sim.step":
        model = StepRequest(**req.payload)
        step = store.step(model.episode_id, model.observation, model.action, model.reward, model.done, model.notes)
        if not step:
            raise HTTPException(status_code=404, detail=f"Episode not found: {model.episode_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"step": step},
        ).model_dump()

    if action == "sim.episode_end":
        model = EpisodeEndRequest(**req.payload)
        episode = store.episode_end(model.episode_id, model.outcome, model.summary)
        if not episode:
            raise HTTPException(status_code=404, detail=f"Episode not found: {model.episode_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"episode": episode},
        ).model_dump()

    if action == "sim.replay_create":
        model = ReplayCreateRequest(**req.payload)
        replay = store.replay_create(model.episode_id)
        if not replay:
            raise HTTPException(status_code=404, detail=f"Episode not found: {model.episode_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"replay": replay},
        ).model_dump()

    if action == "sim.replay_get":
        model = ReplayGetRequest(**req.payload)
        replay = store.replay_get(model.replay_id)
        if not replay:
            raise HTTPException(status_code=404, detail=f"Replay not found: {model.replay_id}")
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data={"replay": replay},
        ).model_dump()

    if action == "sim.dataset_list":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=store.dataset_export(),
        ).model_dump()

    if action == "sim.dataset_export":
        model = DatasetExportRequest(**req.payload)
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=store.dataset_export(model.episode_id),
        ).model_dump()

    if action == "sim.status":
        return PluginResponse(
            plugin=settings.plugin_name,
            action=req.type,
            data=store.status(),
        ).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
