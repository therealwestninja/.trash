# Controller Backend Scaffold

This patch adds a reference backend scaffold for the Controller Team so the web interface can stop relying on heuristics and switch to a strict backend contract.

## Added entrypoint

- `backend/controller_contract_app.py`

Run it with:

```bash
uvicorn backend.controller_contract_app:app --host 0.0.0.0 --port 8001
```

## Implemented modules

- `backend/controller_contract/state_manager.py`
- `backend/controller_contract/command_router.py`
- `backend/controller_contract/event_bus.py`
- `backend/controller_contract/safety_manager.py`
- `backend/controller_contract/session_manager.py`
- `backend/controller_contract/plugin_registry.py`
- `backend/controller_contract/bridges.py`
- `backend/controller_contract/models.py`

## Endpoint contract

- `GET /state` — full authoritative UI bootstrap payload
- `GET /health` — lightweight status
- `GET /capabilities` — plugin and transport exposure
- `POST /execute` — async command acknowledgement
- `WS /ws` — realtime event stream
- `POST /safety/estop`
- `POST /safety/clear_estop`

## What this scaffold demonstrates

- backend-authoritative command policy
- fail-closed gating when safety triggers
- unique command IDs with lifecycle events
- heartbeat messages over WebSocket
- simulation adapter parity for frontend wiring
- plugin capability exposure for Sweetie-Bot integration

## Integration notes

This scaffold is intentionally isolated from the current production `backend/main.py` so the Controller Team can merge pieces incrementally.

Recommended merge order:

1. `models.py`
2. `state_manager.py`
3. `safety_manager.py`
4. `event_bus.py`
5. `command_router.py`
6. route wiring into existing FastAPI app
7. swap simulation bridge for real GO2 adapter

## Example `/state` response shape

```json
{
  "api_version": "1.2.0",
  "hardware": {"mode": "simulation"},
  "robot": {"platform": "unitree_go2"},
  "bridge": {"connected": true},
  "session": {"active": false, "operator_id": null, "active_connections": 0},
  "command_policy": {"allowed_categories": ["motion", "behavior", "mission", "plugin", "body", "script", "arm", "bt", "always"], "restricted": false},
  "simulation": {"active": true},
  "telemetry": {
    "battery_level": 100.0,
    "motion_state": "idle",
    "position": {"x": 0.0, "y": 0.0, "yaw": 0.0},
    "docking_state": "undocked",
    "safety_flags": []
  },
  "plugins": {
    "sweetie_bot": {"enabled": true, "features": ["autonomy", "social", "peer", "dock", "memory"], "health": "healthy"}
  },
  "timestamp": 0.0
}
```
