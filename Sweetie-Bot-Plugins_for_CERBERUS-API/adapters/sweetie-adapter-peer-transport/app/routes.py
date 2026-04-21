from fastapi import APIRouter
from app.services import register_peer, send, get_state

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "adapter": "peer_transport"}

@router.post("/execute")
def execute(req: dict):
    t = (req or {}).get("type", "").strip().lower()
    p = (req or {}).get("payload", {}) or {}
    if t == "adapter.peer.register_peer":
        return {"ok": True, "data": register_peer(p)}
    if t == "adapter.peer.send":
        return {"ok": True, "data": send(p)}
    if t == "adapter.peer.get_state":
        return {"ok": True, "data": get_state()}
    return {"ok": False, "error": f"unsupported action: {t}"}
