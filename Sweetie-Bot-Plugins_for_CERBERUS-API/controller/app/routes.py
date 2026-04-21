from fastapi import APIRouter
from app.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
def health():
    return {"status": "ok", "service": "sweetie-controller", "version": "0.1.0"}


@router.post("/orchestrate")
def orchestrate(event: dict):
    return orchestrator.handle_event(event)
