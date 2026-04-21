from fastapi import APIRouter
from app.services import set_level, set_charging, get_state

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "adapter": "battery"}

@router.post("/execute")
def execute(req: dict):
    t = (req or {}).get("type", "").strip().lower()
    p = (req or {}).get("payload", {}) or {}
    if t == "adapter.battery.set_level":
        return {"ok": True, "data": set_level(p.get("level", 1.0))}
    if t == "adapter.battery.set_charging":
        return {"ok": True, "data": set_charging(p.get("charging", False))}
    if t == "adapter.battery.get_state":
        return {"ok": True, "data": get_state()}
    return {"ok": False, "error": f"unsupported action: {t}"}
