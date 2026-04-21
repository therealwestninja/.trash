from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import TranscribeRequest, ProcessUtteranceRequest, SetDefaultsRequest
from app.services.stt import transcribe, process_utterance, list_providers, set_defaults, get_defaults, status
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
    if t == "stt.transcribe":
        m = TranscribeRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"transcription": transcribe(m.transcript,m.audio_reference,m.provider,m.language,m.metadata)}).model_dump()
    if t == "stt.process_utterance":
        m = ProcessUtteranceRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"utterance": process_utterance(m.transcript,m.speaker_id,m.provider,m.language,m.metadata)}).model_dump()
    if t == "stt.list_providers":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"providers": list_providers()}).model_dump()
    if t == "stt.set_defaults":
        m = SetDefaultsRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"defaults": set_defaults(m.model_dump())}).model_dump()
    if t == "stt.get_defaults":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"defaults": get_defaults()}).model_dump()
    if t == "stt.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
