from fastapi import APIRouter
from app.services import speak, inject_transcript, get_state

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "adapter": "audio"}

@router.post("/execute")
def execute(req: dict):
    t = (req or {}).get("type", "").strip().lower()
    p = (req or {}).get("payload", {}) or {}
    if t == "adapter.audio.speak":
        return {"ok": True, "data": speak(p)}
    if t == "adapter.audio.inject_transcript":
        return {"ok": True, "data": inject_transcript(p)}
    if t == "adapter.audio.get_state":
        return {"ok": True, "data": get_state()}
    return {"ok": False, "error": f"unsupported action: {t}"}
