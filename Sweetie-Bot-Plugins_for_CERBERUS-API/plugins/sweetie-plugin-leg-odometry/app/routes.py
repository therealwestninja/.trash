from fastapi import APIRouter
from app.models import ExecuteRequest
from app.state import state

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}

@router.post("/execute")
def execute(req: ExecuteRequest):

    if req.type == "odom.update":
        return state.update(
            req.payload.get("vx",0),
            req.payload.get("vy",0),
            req.payload.get("yaw_rate",0),
            req.payload.get("dt",1)
        )

    if req.type == "odom.get":
        return state.get()

    if req.type == "odom.reset":
        return state.reset()

    if req.type == "odom.status":
        return {"active":True}

    return {"error":"unknown"}
