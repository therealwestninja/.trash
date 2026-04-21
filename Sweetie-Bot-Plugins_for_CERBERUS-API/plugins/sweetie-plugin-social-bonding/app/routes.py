from fastapi import APIRouter, HTTPException
from app.models import RegisterHumanRequest, ObserveHumanRequest, UpdateRelationshipRequest, RankAttentionRequest
from app.services.bonding import register_human, observe_human, update_relationship, get_best_friend, list_humans, rank_attention, decay, reset, status
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()
@router.get("/health")
def health(): return {"status":"ok"}
@router.get("/manifest")
def manifest(): return load_manifest()
@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type.strip().lower()
    try:
        if t == "bonding.register_human":
            m = RegisterHumanRequest(**req.payload); return PluginResponse(plugin="social-bonding", action=req.type, data={"human": register_human(m.human_id,m.name,m.tier,m.tags)}).model_dump()
        if t == "bonding.observe_human":
            m = ObserveHumanRequest(**req.payload); return PluginResponse(plugin="social-bonding", action=req.type, data={"human": observe_human(m.human_id,m.event,m.closeness_m,m.tags)}).model_dump()
        if t == "bonding.update_relationship":
            m = UpdateRelationshipRequest(**req.payload); return PluginResponse(plugin="social-bonding", action=req.type, data={"human": update_relationship(m.human_id,m.familiarity_delta,m.trust_delta,m.comfort_delta,m.affection_delta)}).model_dump()
        if t == "bonding.get_best_friend":
            return PluginResponse(plugin="social-bonding", action=req.type, data={"best_friend": get_best_friend()}).model_dump()
        if t == "bonding.list_humans":
            return PluginResponse(plugin="social-bonding", action=req.type, data={"humans": list_humans()}).model_dump()
        if t == "bonding.rank_attention":
            m = RankAttentionRequest(**req.payload); return PluginResponse(plugin="social-bonding", action=req.type, data={"ranked_humans": rank_attention(m.visible_human_ids)}).model_dump()
        if t == "bonding.decay":
            return PluginResponse(plugin="social-bonding", action=req.type, data=decay()).model_dump()
        if t == "bonding.reset":
            return PluginResponse(plugin="social-bonding", action=req.type, data=reset()).model_dump()
        if t == "bonding.status":
            return PluginResponse(plugin="social-bonding", action=req.type, data=status()).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail="human_not_found")
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
