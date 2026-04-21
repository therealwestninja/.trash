from fastapi import APIRouter, HTTPException
from app.models import RegisterRoutesRequest, PatrolMissionRequest, ChainExecuteRequest
from app.services.state import state
from app.services.http_clients import call_execute
from app.config import settings
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()

def remember(entry: dict):
    state.history.append(entry)
    state.history = state.history[-30:]

@router.get("/health")
def health():
    return {"status":"ok","plugin":settings.plugin_name,"version":settings.plugin_version}

@router.get("/manifest")
def manifest():
    return load_manifest()

@router.post("/execute")
async def execute(req: ExecuteRequest):
    t = req.type.strip().lower()

    if t == "runtime.register_routes":
        m = RegisterRoutesRequest(**req.payload)
        for k, v in m.model_dump().items():
            if v:
                state.routes[k.replace("_url","")] = v
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"routes": state.routes}).model_dump()

    if t == "runtime.follow_best_friend":
        bf = await call_execute(state.routes["bonding"], {"type":"bonding.get_best_friend","payload":{}})
        best = ((bf or {}).get("data") or {}).get("best_friend")
        if not best:
            raise HTTPException(status_code=404, detail="best_friend_not_found")
        action = {"type":"action.dispatch","payload":{"action_name":"follow_operator","payload_override":{"target_id": best["human_id"]}}}
        safety = await call_execute(state.routes["safety"], {"type":"safety.evaluate_action","payload":{"action": action, "context": {}}})
        result = {"best_friend": best, "action": action, "safety": safety}
        remember(result)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=result).model_dump()

    if t == "runtime.dock_cycle":
        payload = req.payload or {}
        seek = await call_execute(state.routes["docking"], {"type":"docking.seek_dock","payload": payload})
        result = {"seek": seek}
        if ((seek or {}).get("data") or {}).get("should_dock"):
            suggested = (((seek or {}).get("data") or {}).get("suggested_action"))
            if suggested and suggested.get("type") == "navigation.plan_to_point":
                nav = await call_execute(state.routes["navigation"], suggested)
                result["navigation"] = nav
        remember(result)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=result).model_dump()

    if t == "runtime.patrol_mission":
        m = PatrolMissionRequest(**req.payload)
        waypoints = m.waypoints[:]
        if m.loop and waypoints:
            waypoints.append(waypoints[0])
        result = {"mission_payload":{"type":"nav.follow_waypoints","payload":{"waypoints": waypoints}}}
        remember(result)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=result).model_dump()

    if t == "runtime.peer_status_ping":
        peer_id = req.payload.get("peer_id")
        if not peer_id:
            raise HTTPException(status_code=400, detail="peer_id_required")
        message = await call_execute(state.routes["crusader"], {
            "type":"crusader.send_message",
            "payload":{"peer_id": peer_id, "message_type":"status_ping", "payload": req.payload.get("payload", {})}
        })
        remember({"peer_ping": message})
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"message": message}).model_dump()

    if t == "runtime.chain_execute":
        m = ChainExecuteRequest(**req.payload)
        if m.chain_name == "follow_best_friend":
            nested = await execute(ExecuteRequest(type="runtime.follow_best_friend", payload=m.payload))
            return nested
        if m.chain_name == "dock_cycle":
            nested = await execute(ExecuteRequest(type="runtime.dock_cycle", payload=m.payload))
            return nested
        if m.chain_name == "peer_status_ping":
            nested = await execute(ExecuteRequest(type="runtime.peer_status_ping", payload=m.payload))
            return nested
        raise HTTPException(status_code=400, detail=f"unknown_chain_name:{m.chain_name}")

    if t == "runtime.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"routes": state.routes, "history": state.history[-10:]}).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
