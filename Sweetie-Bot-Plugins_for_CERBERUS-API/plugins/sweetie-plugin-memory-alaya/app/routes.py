from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import StoreMemoryRequest, QueryMemoryRequest, ConsolidateRequest, IdRequest
from app.services.store import store
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
    if t == "memory.store_episode":
        m = StoreMemoryRequest(**req.payload)
        meta = {**m.metadata}
        if m.relationship_tier:
            meta["relationship_tier"] = m.relationship_tier
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"memory": store.store("episode", m.text, m.tags, m.source, m.salience, meta, m.ttl_days)}).model_dump()
    if t == "memory.store_fact":
        m = StoreMemoryRequest(**req.payload)
        meta = {**m.metadata}
        if m.relationship_tier:
            meta["relationship_tier"] = m.relationship_tier
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"memory": store.store("fact", m.text, m.tags, m.source, m.salience, meta, m.ttl_days)}).model_dump()
    if t == "memory.query":
        m = QueryMemoryRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"results": store.query(m.text, m.limit, m.tags, m.preferred_relationship_tiers)}).model_dump()
    if t == "memory.consolidate":
        m = ConsolidateRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"created": store.consolidate(m.min_tag_overlap)}).model_dump()
    if t == "memory.get":
        m = IdRequest(**req.payload); res = store.get(m.id)
        if not res: raise HTTPException(status_code=404, detail="memory_not_found")
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"memory": res}).model_dump()
    if t == "memory.list":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"results": store.list()}).model_dump()
    if t == "memory.delete":
        m = IdRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"deleted": store.delete(m.id), "id": m.id}).model_dump()
    if t == "memory.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=store.status()).model_dump()
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
