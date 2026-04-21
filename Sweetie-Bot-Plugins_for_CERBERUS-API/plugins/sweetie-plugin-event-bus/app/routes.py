from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import PublishEventRequest, SubscribeRequest, PollRequest
from app.services.bus import subscribe, unsubscribe, publish, poll, recent, clear, status
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
    if t == "event.publish":
        m = PublishEventRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=publish(m.topic,m.source,m.payload,m.tags)).model_dump()
    if t == "event.subscribe":
        m = SubscribeRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=subscribe(m.subscriber_id,m.topics)).model_dump()
    if t == "event.unsubscribe":
        sid = req.payload["subscriber_id"]; return PluginResponse(plugin=settings.plugin_name, action=req.type, data=unsubscribe(sid)).model_dump()
    if t == "event.poll":
        m = PollRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data=poll(m.subscriber_id,m.limit)).model_dump()
    if t == "event.recent":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"events": recent(int(req.payload.get("limit",25)))}).model_dump()
    if t == "event.clear":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=clear()).model_dump()
    if t == "event.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
