from __future__ import annotations

import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from backend.controller_contract.bridges import SimulationControlBridge
from backend.controller_contract.command_router import CommandRouter
from backend.controller_contract.command_tracker import CommandTracker
from backend.controller_contract.event_bus import EventBus
from backend.controller_contract.models import CapabilityResponse, CommandHistoryResponse, ExecuteCommandRequest
from backend.controller_contract.plugin_registry import PluginRegistry
from backend.controller_contract.safety_manager import SafetyManager
from backend.controller_contract.session_manager import SessionManager
from backend.controller_contract.state_manager import StateManager

API_VERSION = '1.2.0'


@asynccontextmanager
async def lifespan(app: FastAPI):
    bridge = SimulationControlBridge()
    session_manager = SessionManager()
    safety_manager = SafetyManager()
    plugin_registry = PluginRegistry()
    event_bus = EventBus()
    command_tracker = CommandTracker()
    state_manager = StateManager(
        bridge=bridge,
        session_manager=session_manager,
        safety_manager=safety_manager,
        plugin_registry=plugin_registry,
        command_tracker=command_tracker,
        api_version=API_VERSION,
    )
    router = CommandRouter(
        bridge=bridge,
        state_manager=state_manager,
        safety_manager=safety_manager,
        event_bus=event_bus,
        command_tracker=command_tracker,
    )
    await router.start()

    app.state.bridge = bridge
    app.state.session_manager = session_manager
    app.state.safety_manager = safety_manager
    app.state.plugin_registry = plugin_registry
    app.state.event_bus = event_bus
    app.state.command_tracker = command_tracker
    app.state.state_manager = state_manager
    app.state.command_router = router

    async def heartbeat_loop() -> None:
        while True:
            await asyncio.sleep(5)
            await event_bus.broadcast_heartbeat()

    async def telemetry_loop() -> None:
        while True:
            await asyncio.sleep(1)
            state = await state_manager.get_state()
            await event_bus.publish('telemetry', state.telemetry.model_dump())
            await event_bus.publish('system_state', state.model_dump(mode='json'))

    heartbeat_task = asyncio.create_task(heartbeat_loop())
    telemetry_task = asyncio.create_task(telemetry_loop())
    try:
        yield
    finally:
        for task in (heartbeat_task, telemetry_task):
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await router.stop()


app = FastAPI(
    title='CERBERUS Controller Contract Scaffold',
    version=API_VERSION,
    description='Reference backend scaffold for the Controller Team contract.',
    lifespan=lifespan,
)


@app.get('/')
async def root():
    return JSONResponse({'ok': True, 'service': 'cerberus-controller-contract', 'api_version': API_VERSION})


@app.get('/health')
async def health():
    return await app.state.state_manager.get_health()


@app.get('/state')
async def state():
    return await app.state.state_manager.get_state()


@app.get('/capabilities')
async def capabilities():
    state = await app.state.state_manager.get_state()
    return CapabilityResponse(api_version=state.api_version, plugins=state.plugins)


@app.get('/commands')
async def commands(limit: int = 20):
    items = await app.state.command_tracker.history(limit=max(1, min(limit, 100)))
    runtime = await app.state.command_tracker.runtime()
    return CommandHistoryResponse(
        items=items,
        total=runtime.total_commands_seen,
        active_command_id=runtime.active_command_id,
        queue_depth=runtime.queue_depth,
    )


@app.get('/commands/{command_id}')
async def command_by_id(command_id: str):
    record = await app.state.command_tracker.get(command_id)
    if record is None:
        raise HTTPException(status_code=404, detail='command_not_found')
    return record


@app.post('/execute')
async def execute(request: ExecuteCommandRequest):
    return await app.state.command_router.enqueue(request)


@app.post('/safety/estop')
async def trigger_estop():
    fault = app.state.safety_manager.trigger_estop()
    state = await app.state.state_manager.get_state()
    await app.state.event_bus.publish('fault', fault.model_dump())
    await app.state.event_bus.publish('system_state', state.model_dump(mode='json'))
    return {'ok': True, 'fault': fault}


@app.post('/safety/clear_estop')
async def clear_estop():
    app.state.safety_manager.clear_estop()
    state = await app.state.state_manager.get_state()
    await app.state.event_bus.publish('system_state', state.model_dump(mode='json'))
    return {'ok': True}


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    operator_id = websocket.query_params.get('operator_id')
    replay = websocket.query_params.get('replay', '1') != '0'
    await app.state.event_bus.register_client(websocket)
    await app.state.session_manager.connect(operator_id)
    state = await app.state.state_manager.get_state()
    history = await app.state.command_tracker.history(limit=10)
    await app.state.event_bus.send_snapshot(websocket, {
        'state': state.model_dump(mode='json'),
        'recent_commands': [item.model_dump(mode='json') for item in history],
    })
    if replay:
        await app.state.event_bus.replay_recent(websocket, limit=10)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await app.state.session_manager.disconnect()
        await app.state.event_bus.unregister_client(websocket)


def main() -> None:
    import uvicorn
    uvicorn.run('backend.controller_contract_app:app', host='0.0.0.0', port=8001, reload=False)


if __name__ == '__main__':
    main()
