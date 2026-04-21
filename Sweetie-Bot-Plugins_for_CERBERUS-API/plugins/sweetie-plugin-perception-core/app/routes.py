from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import IngestRequest, IdRequest
from app.services.tracker import ingest, list_tracks, get_track, export_attention_candidates, reset
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok","plugin":settings.plugin_name,"version":settings.plugin_version}

@router.get("/manifest")
def manifest():
    return load_manifest()

@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type.strip().lower()
    if t == "perception.ingest":
        m = IngestRequest(**req.payload)
        tracks, events = ingest(m.detections, m.source, m.scene)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"tracks":tracks,"events":events}).model_dump()
    if t == "perception.track_list":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"tracks":list_tracks()}).model_dump()
    if t == "perception.track_get":
        m = IdRequest(**req.payload); tr = get_track(m.track_id)
        if not tr: raise HTTPException(status_code=404, detail="track_not_found")
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"track":tr}).model_dump()
    if t == "perception.export_attention_candidates":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"candidates":export_attention_candidates()}).model_dump()
    if t == "perception.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=reset()).model_dump()
    if t == "perception.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"track_count":len(list_tracks())}).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
