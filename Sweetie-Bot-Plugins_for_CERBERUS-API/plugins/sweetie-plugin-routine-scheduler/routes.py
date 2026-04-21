from fastapi import APIRouter
from models import ExecuteRequest, PluginResponse
from core import add, remove, list_all, tick
from state import state

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}

@router.post("/execute")
def execute(req: ExecuteRequest):
    t = req.type
    p = req.payload

    if t == "routine.add":
        return PluginResponse(plugin="routine", action=t, data=add(p["name"], p["interval"])).model_dump()

    if t == "routine.remove":
        return PluginResponse(plugin="routine", action=t, data=remove(p["name"])).model_dump()

    if t == "routine.list":
        return PluginResponse(plugin="routine", action=t, data={"routines":list_all()}).model_dump()

    if t == "routine.tick":
        return PluginResponse(plugin="routine", action=t, data=tick()).model_dump()

    if t == "routine.reset":
        state.routines.clear()
        return PluginResponse(plugin="routine", action=t, data={"reset":True}).model_dump()

    if t == "routine.status":
        return PluginResponse(plugin="routine", action=t, data={"count":len(state.routines)}).model_dump()

    return PluginResponse(plugin="routine", action=t, data={}).model_dump()
