from fastapi import APIRouter, HTTPException
from app.models import RegisterPeerRequest, UpdateLinkRequest, SendMessageRequest, PeerIdRequest
from app.services.link import register_peer, update_link, send_message, list_peers, get_state, reset, choose_transport_for, state
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
        if t == "crusader.register_peer":
            m = RegisterPeerRequest(**req.payload); return PluginResponse(plugin="crusader-link", action=req.type, data={"peer": register_peer(m.peer_id,m.name,m.role,m.transports)}).model_dump()
        if t == "crusader.update_link":
            m = UpdateLinkRequest(**req.payload); return PluginResponse(plugin="crusader-link", action=req.type, data={"peer": update_link(m.peer_id,m.transports,m.battery,m.status)}).model_dump()
        if t == "crusader.send_message":
            m = SendMessageRequest(**req.payload); return PluginResponse(plugin="crusader-link", action=req.type, data={"message": send_message(m.peer_id,m.message_type,m.payload)}).model_dump()
        if t == "crusader.list_peers":
            return PluginResponse(plugin="crusader-link", action=req.type, data={"peers": list_peers()}).model_dump()
        if t == "crusader.choose_transport":
            m = PeerIdRequest(**req.payload); p = state.peers.get(m.peer_id)
            if not p: raise KeyError("peer_not_found")
            return PluginResponse(plugin="crusader-link", action=req.type, data={"peer_id": m.peer_id, "chosen_transport": choose_transport_for(p.transports)}).model_dump()
        if t == "crusader.get_state":
            return PluginResponse(plugin="crusader-link", action=req.type, data=get_state()).model_dump()
        if t == "crusader.reset":
            return PluginResponse(plugin="crusader-link", action=req.type, data=reset()).model_dump()
        if t == "crusader.status":
            return PluginResponse(plugin="crusader-link", action=req.type, data=get_state()).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail="peer_not_found")
    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
