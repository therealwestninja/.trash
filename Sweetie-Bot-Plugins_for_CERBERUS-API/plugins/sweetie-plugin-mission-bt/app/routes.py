from fastapi import APIRouter
from app.models import ExecuteRequest
from app.engine import engine

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}

@router.post("/execute")
def execute(req: ExecuteRequest):

    if req.type == "mission.start":
        return engine.start(req.payload)

    if req.type == "mission.tick":
        return engine.tick()

    if req.type == "mission.stop":
        return engine.stop()

    if req.type == "mission.status":
        return {"active": engine.current}

    return {"error":"unknown"}
