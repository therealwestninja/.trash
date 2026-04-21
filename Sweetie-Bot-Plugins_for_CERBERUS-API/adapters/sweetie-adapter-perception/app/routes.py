from fastapi import APIRouter
from app.services import state, inject_best_friend, inject_public_person, get_state

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "adapter": "perception"}

@router.post("/execute")
def execute(req: dict):
    t = (req or {}).get("type", "").strip().lower()
    p = (req or {}).get("payload", {}) or {}
    if t == "adapter.perception.inject_best_friend":
        return {"ok": True, "data": inject_best_friend(p)}
    if t == "adapter.perception.inject_public_person":
        return {"ok": True, "data": inject_public_person(p)}
    if t == "adapter.perception.state":
        return {"ok": True, "data": get_state()}
    return {"ok": False, "error": f"unsupported action: {t}"}
