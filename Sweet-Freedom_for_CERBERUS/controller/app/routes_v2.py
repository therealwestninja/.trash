from fastapi import APIRouter, HTTPException, Response, WebSocket, WebSocketDisconnect

from .api_models import (
    CapabilityRegistryResponse,
    ControlSourceRequest,
    DiagnosticsResponse,
    GoalCancelRequest,
    HealthResponse,
    OperatorTextRequest,
    PresenceTickResponse,
    QuickActionRequest,
    ReplayLoadRequest,
    ReplayStateResponse,
    SessionAcquireRequest,
    SessionCheckinRequest,
    SessionReleaseRequest,
    SessionSummaryResponse,
    SimpleActionResponse,
)
from .capability_registry import capability_registry
from .event_helpers import make_event
from .event_publisher import publish_named_event, publish_runtime_bundle, publish_session_bundle
from .event_stream import event_stream
from .quick_actions import resolve_quick_action
from .runtime_manager import runtime_manager
from .session_recorder import session_recorder
from .session_replay import session_replay

router = APIRouter()


@router.post("/sweetie/operator_text")
async def operator_text(payload: OperatorTextRequest):
    text = payload.text or ""
    state = runtime_manager.process_text(text, requested_by="ui")
    await publish_runtime_bundle(state)
    return state


@router.post("/sweetie/action/quick")
async def quick_action(payload: QuickActionRequest):
    text = resolve_quick_action(payload.action)
    state = runtime_manager.process_text(text, requested_by="quick_action")
    await publish_runtime_bundle(state)
    await publish_named_event(
        "quick_action",
        {
            "requested": payload.action,
            "resolved_text": text,
            "goal": state.get("active_goal"),
            "feedback": state.get("last_feedback"),
            "result": state.get("goal_result"),
        },
    )
    return state


@router.post("/sweetie/action/cancel")
async def cancel_action(payload: GoalCancelRequest):
    state = runtime_manager.cancel_goal(payload.goal_id, requested_by=payload.requested_by)
    if state is None:
        raise HTTPException(status_code=404, detail="goal not found")
    await publish_runtime_bundle(state)
    await publish_named_event(
        "goal_canceled",
        {
            "goal": state.get("active_goal"),
            "feedback": state.get("last_feedback"),
            "result": state.get("goal_result"),
        },
    )
    return state


@router.post("/sweetie/control/lock")
async def lock_control_source(payload: ControlSourceRequest):
    ok = runtime_manager.lock_source(payload.source)
    if not ok:
        raise HTTPException(status_code=404, detail="source not found")
    data = runtime_manager.get_state().get("command_mux")
    await publish_named_event("control_source", data)
    return data


@router.post("/sweetie/control/unlock")
async def unlock_control_source(payload: ControlSourceRequest):
    ok = runtime_manager.unlock_source(payload.source)
    if not ok:
        raise HTTPException(status_code=404, detail="source not found")
    data = runtime_manager.get_state().get("command_mux")
    await publish_named_event("control_source", data)
    return data


@router.post("/sweetie/lifecycle/recover")
async def recover_lifecycle():
    state = runtime_manager.recover_lifecycle()
    await publish_runtime_bundle(state)
    return state


@router.post("/sweetie/safety/arm")
async def arm_system():
    state = runtime_manager.arm_system()
    await publish_runtime_bundle(state)
    await publish_named_event("safety_event", {"event": "system_armed", "safety": state.get("safety")})
    return state


@router.post("/sweetie/safety/disarm")
async def disarm_system():
    state = runtime_manager.disarm_system()
    await publish_runtime_bundle(state)
    await publish_named_event("safety_event", {"event": "system_disarmed", "safety": state.get("safety")})
    return state


@router.get("/sweetie/diagnostics", response_model=DiagnosticsResponse)
async def diagnostics():
    return runtime_manager.get_state().get("diagnostics")


@router.get("/sweetie/capabilities", response_model=CapabilityRegistryResponse)
async def capabilities():
    return capability_registry.snapshot()


@router.get("/sweetie/capabilities/{capability_id}")
async def capability_detail(capability_id: str):
    capability = capability_registry.get_capability(capability_id)
    if capability is None:
        raise HTTPException(status_code=404, detail="capability not found")
    return capability


@router.get("/sweetie/recording/export")
async def export_recording():
    return Response(content=session_recorder.export_jsonl(), media_type="application/x-ndjson")


@router.post("/sweetie/recording/clear", response_model=SimpleActionResponse)
async def clear_recording():
    session_recorder.clear()
    return SimpleActionResponse(ok=True, message="recording cleared")


@router.post("/sweetie/replay/load", response_model=ReplayStateResponse)
async def replay_load(payload: ReplayLoadRequest):
    if not payload.jsonl.strip():
        raise HTTPException(status_code=400, detail="jsonl is required")
    state = session_replay.load_jsonl(payload.jsonl)
    await publish_named_event("replay_state", state)
    return state


@router.post("/sweetie/replay/step")
async def replay_step():
    event = session_replay.step()
    if event is None:
        raise HTTPException(status_code=404, detail="no replay event available")
    replay = session_replay.snapshot()
    await publish_named_event("replay_event", event)
    await publish_named_event("replay_state", replay)
    return {"event": event, "replay": replay}


@router.get("/sweetie/replay/state", response_model=ReplayStateResponse)
async def replay_state():
    return session_replay.snapshot()


@router.post("/sweetie/replay/clear", response_model=ReplayStateResponse)
async def replay_clear():
    state = session_replay.clear()
    await publish_named_event("replay_state", state)
    return state


@router.post("/sweetie/session/acquire")
async def session_acquire(payload: SessionAcquireRequest):
    lease = runtime_manager.acquire_session(payload.owner)
    current = runtime_manager.get_state()
    await publish_session_bundle(current.get("session"), current.get("lifecycle"))
    return lease


@router.post("/sweetie/session/checkin")
async def session_checkin(payload: SessionCheckinRequest):
    lease = runtime_manager.session_checkin(payload.lease_id)
    if lease is None:
        raise HTTPException(status_code=404, detail="lease not found")
    current = runtime_manager.get_state()
    await publish_session_bundle(current.get("session"), current.get("lifecycle"))
    return lease


@router.post("/sweetie/session/release")
async def session_release(payload: SessionReleaseRequest):
    ok = runtime_manager.release_session(payload.lease_id)
    if not ok:
        raise HTTPException(status_code=404, detail="lease not found")
    current = runtime_manager.get_state()
    await publish_session_bundle(current.get("session"), current.get("lifecycle"))
    return SimpleActionResponse(ok=True, message="session released")


@router.get("/sweetie/session/state", response_model=SessionSummaryResponse)
async def session_state():
    return runtime_manager.get_state().get("session")


@router.get("/sweetie/runtime_full_state")
async def runtime_full_state():
    return runtime_manager.get_state()


@router.post("/sweetie/presence_tick", response_model=PresenceTickResponse)
async def presence_tick():
    presence = runtime_manager.tick_presence()
    await publish_named_event("presence_update", {"presence": presence, "state": runtime_manager.get_state()})
    return presence


@router.post("/sweetie/safety/estop")
async def trigger_estop():
    safety = runtime_manager.trigger_estop()
    state = runtime_manager.get_state()
    await publish_named_event("safety_event", {"event": "estop_triggered", "safety": safety})
    await publish_runtime_bundle(state)
    return safety


@router.post("/sweetie/safety/clear_estop")
async def clear_estop():
    safety = runtime_manager.clear_estop()
    state = runtime_manager.get_state()
    await publish_named_event("safety_event", {"event": "estop_cleared", "safety": safety})
    await publish_runtime_bundle(state)
    return safety


@router.websocket("/sweetie/ws")
async def sweetie_ws(websocket: WebSocket):
    await event_stream.connect(websocket)
    await websocket.send_json(make_event("runtime_state", runtime_manager.get_state()))
    try:
        while True:
            message = await websocket.receive_text()
            if message.lower() == "ping":
                await websocket.send_json(make_event("heartbeat", {"status": "ok"}))
    except WebSocketDisconnect:
        await event_stream.disconnect(websocket)


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


@router.get("/ready", response_model=HealthResponse)
async def ready():
    return HealthResponse(status="ready")
