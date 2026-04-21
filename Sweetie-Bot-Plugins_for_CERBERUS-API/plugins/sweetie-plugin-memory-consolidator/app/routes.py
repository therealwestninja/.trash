from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import EpisodeIngestRequest, LocationIngestRequest, BehaviorOutcomeIngestRequest
from app.services.consolidator import ingest_episode, ingest_location, ingest_behavior_outcome, consolidate, get_knowledge, get_profile, reset, status
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
    if t == "consolidator.ingest_episode":
        m = EpisodeIngestRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"entry": ingest_episode(m.text,m.tags,m.salience,m.relationship_tier,m.autonomy_mode)}).model_dump()
    if t == "consolidator.ingest_location":
        m = LocationIngestRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"entry": ingest_location(m.name,m.position,m.confidence,m.metadata)}).model_dump()
    if t == "consolidator.ingest_behavior_outcome":
        m = BehaviorOutcomeIngestRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"entry": ingest_behavior_outcome(m.behavior,m.reward,m.outcome,m.tags,m.relationship_tier,m.autonomy_mode)}).model_dump()
    if t == "consolidator.consolidate":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=consolidate()).model_dump()
    if t == "consolidator.get_knowledge":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"knowledge": get_knowledge()}).model_dump()
    if t == "consolidator.get_profile":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"profile": get_profile()}).model_dump()
    if t == "consolidator.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=reset()).model_dump()
    if t == "consolidator.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
