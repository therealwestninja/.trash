from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import IngestCandidatesRequest, SetBiasRequest
from app.services.attention import ingest_candidates, rank_candidates, select_focus, set_bias, status, reset
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
    auto_mode = req.payload.get("autonomy_mode")
    if t == "attention.ingest_candidates":
        m = IngestCandidatesRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"ranked_candidates": ingest_candidates([c.model_dump() for c in m.candidates], auto_mode)}).model_dump()
    if t == "attention.rank":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"ranked_candidates": rank_candidates(auto_mode)}).model_dump()
    if t == "attention.select_focus":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"focus": select_focus(auto_mode)}).model_dump()
    if t == "attention.set_bias":
        m = SetBiasRequest(**req.payload); return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": set_bias(m.model_dump())}).model_dump()
    if t == "attention.get_focus":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"focus": status()["current_focus"]}).model_dump()
    if t == "attention.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=reset()).model_dump()
    if t == "attention.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
