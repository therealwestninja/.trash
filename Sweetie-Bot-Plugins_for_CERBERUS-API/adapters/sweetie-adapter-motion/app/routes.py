from fastapi import APIRouter
from app.services import translate_motion, report_state

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "adapter": "motion"}

@router.post("/execute")
def execute(req: dict):
    t = (req or {}).get("type", "").strip().lower()
    p = (req or {}).get("payload", {}) or {}
    if t == "adapter.motion.translate":
        return {"ok": True, "data": translate_motion(p)}
    if t == "adapter.motion.report_state":
        return {"ok": True, "data": report_state()}
    return {"ok": False, "error": f"unsupported action: {t}"}
