# sweetie-plugin-nav2-pathing

A standalone navigation plugin that gives the CERBERUS controller a stable, reusable pathing layer.

It is designed as the **lowest-hanging-fruit navigation adapter**:
- easy for the controller to call over HTTP
- easy for CERBERUS API to understand
- ready to forward requests into a future real Nav2 / ROS2 stack

## What it does

This plugin exposes a simple contract for:
- `nav.goal` — send the robot to a point
- `nav.preview_route` — get a controller-friendly route preview
- `nav.follow_waypoints` — send a waypoint chain
- `nav.recovery` — suggest or trigger recovery actions
- `nav.cancel` — cancel the active plan
- `nav.status` — inspect the current navigation state

Right now it ships with a deterministic internal planner so the API contract is usable immediately.
Later, you can turn on forwarding to a ROS2 bridge or real Nav2 backend.

## Why this exists

The CERBERUS controller and API can already issue direct robot commands, but a pathing plugin adds:
- route abstraction above raw motion commands
- waypoint navigation
- controller previews for missions and patrols
- a cleaner stepping stone toward obstacle-aware autonomy
- a stable interface other plugins can call

## Quick start

### Run directly
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7000
```

### Run with Docker
```bash
docker build -t sweetie-plugin-nav2-pathing .
docker run --rm -p 7000:7000 --env-file .env.example sweetie-plugin-nav2-pathing
```

## Health + manifest

```bash
curl http://localhost:7000/health
curl http://localhost:7000/manifest
```

## Main endpoint

`POST /execute`

Body shape:
```json
{
  "type": "nav.goal",
  "payload": {
    "x": 2.5,
    "y": 1.0,
    "yaw": 0.0,
    "frame": "map"
  }
}
```

## Supported execute types

### 1) `nav.goal`
Moves to a single goal and returns a generated path preview.

Example:
```bash
curl -X POST http://localhost:7000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type":"nav.goal",
    "payload":{"x":2.5,"y":1.0,"yaw":0.0,"frame":"map"}
  }'
```

### 2) `nav.preview_route`
Produces a route preview between an origin and destination.

Example:
```json
{
  "type": "nav.preview_route",
  "payload": {
    "start": {"x": 0, "y": 0},
    "goal": {"x": 3, "y": 2},
    "frame": "map"
  }
}
```

### 3) `nav.follow_waypoints`
Takes a list of waypoints and returns a stitched route.

Example:
```json
{
  "type": "nav.follow_waypoints",
  "payload": {
    "frame": "map",
    "waypoints": [
      {"x": 1, "y": 0},
      {"x": 2, "y": 1},
      {"x": 3, "y": 1}
    ]
  }
}
```

### 4) `nav.recovery`
Returns or triggers controller-safe recovery recommendations.

Accepted payload examples:
```json
{"issue": "blocked_front"}
{"issue": "lost_localization"}
{"issue": "narrow_passage"}
```

### 5) `nav.cancel`
Cancels the active internal plan.

### 6) `nav.status`
Returns the active task and the last generated route.

## Controller integration

From the CERBERUS web controller:
```javascript
await fetch("http://localhost:7000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    type: "nav.goal",
    payload: { x: 2.0, y: 0.5, yaw: 0.0, frame: "map" }
  })
}).then(r => r.json())
```

## CERBERUS API integration

The backend can treat this exactly like any other Sweetie plugin:
```python
import requests

resp = requests.post(
    "http://localhost:7000/execute",
    json={
        "type": "nav.follow_waypoints",
        "payload": {
            "frame": "map",
            "waypoints": [{"x": 1, "y": 0}, {"x": 2, "y": 2}]
        },
    },
    timeout=15,
)
print(resp.json())
```

## Forwarding to ROS2 / Nav2 later

Set:
```bash
FORWARD_TO_ROS2=true
ROS2_BRIDGE_URL=http://your-ros2-bridge:7010
```

When enabled, this plugin will:
- preserve the same HTTP contract for CERBERUS
- forward normalized navigation requests to a ROS2 bridge
- keep your controller and API stable while the robotics backend grows

## Project structure

```text
sweetie-plugin-nav2-pathing/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   └── services/
│       ├── planner.py
│       └── ros2_forwarder.py
├── examples/
│   ├── python_client.py
│   └── js_client.js
├── sweetie_plugin_sdk/
│   ├── __init__.py
│   ├── manifest.py
│   └── models.py
├── Dockerfile
├── plugin.yaml
└── README.md
```

## Notes

This is intentionally a **stable contract first** plugin:
- controller-ready now
- easy to test now
- easy to replace with real Nav2 later
- keeps CERBERUS from hardcoding one pathing backend forever
