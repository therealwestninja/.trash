from fastapi import APIRouter

from .orchestrator import handle_text

router = APIRouter()


@router.post("/sweetie/operator_text")
def operator_text(payload: dict):
    text = payload.get("text", "")
    return handle_text(text)


@router.get("/sweetie/runtime_full_state")
def runtime_state():
    return {"status": "running"}
