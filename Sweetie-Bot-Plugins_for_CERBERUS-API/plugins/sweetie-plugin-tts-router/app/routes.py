from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import SpeakRequest, PreviewVoiceRequest, SetDefaultsRequest
from app.services.tts import build_speech, preview_voice, list_voices, set_defaults, get_defaults, status
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
    if t == "tts.speak":
        m = SpeakRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"speech_envelope": build_speech(m.text,m.tone,m.emotion,m.voice,m.provider,m.rate,m.pitch,m.metadata)}).model_dump()
    if t == "tts.preview_voice":
        m = PreviewVoiceRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"speech_envelope": preview_voice(m.voice,m.sample_text)}).model_dump()
    if t == "tts.list_voices":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"voices": list_voices()}).model_dump()
    if t == "tts.set_defaults":
        m = SetDefaultsRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"defaults": set_defaults(m.model_dump())}).model_dump()
    if t == "tts.get_defaults":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"defaults": get_defaults()}).model_dump()
    if t == "tts.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
