# sweetie-plugin-world-model

A reusable shared world-state plugin for the CERBERUS controller ecosystem.

This plugin is the glue between:
- perception plugins
- navigation/pathing plugins
- mission/autonomy plugins
- AI/character logic
- controller UI features

Instead of every subsystem keeping its own private detections, this plugin stores a shared object layer.

## Why this matters

Without a world model:
- detections are one-off events
- missions cannot reason about persistent targets
- navigation cannot reuse semantic object knowledge
- AI interactions have no stable memory of people, pets, doors, charging stations, or hazards

With a world model:
- perception can publish `person`, `door`, `hazard`, `charging_dock`
- controller can inspect and edit live objects
- missions can target known objects
- navigation can query nearby semantic points
- future plugins can use the same environment memory

## Supported execute actions

- `world.upsert_object`
- `world.get_object`
- `world.list_objects`
- `world.delete_object`
- `world.clear`
- `world.observe`
- `world.query_near`
- `world.status`

## Object shape

```json
{
  "id": "dock-1",
  "label": "charging_dock",
  "category": "infrastructure",
  "frame": "map",
  "position": {"x": 4.2, "y": 1.1, "z": 0.0},
  "confidence": 0.97,
  "attributes": {"color": "black", "marker_id": 7},
  "tags": ["dock", "charging"],
  "ttl_seconds": 3600
}
```

## Quick start

### Local
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7000
```

### Docker
```bash
docker build -t sweetie-plugin-world-model .
docker run --rm -p 7000:7000 --env-file .env.example sweetie-plugin-world-model
```

## Health and manifest

```bash
curl http://localhost:7000/health
curl http://localhost:7000/manifest
```

## Examples

### Upsert an object
```bash
curl -X POST http://localhost:7000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "world.upsert_object",
    "payload": {
      "id": "person-001",
      "label": "person",
      "category": "human",
      "frame": "map",
      "position": {"x": 1.2, "y": 3.4, "z": 0.0},
      "confidence": 0.94,
      "attributes": {"name": "operator"},
      "tags": ["operator", "human"]
    }
  }'
```

### Query nearby objects
```json
{
  "type": "world.query_near",
  "payload": {
    "origin": {"x": 1.0, "y": 3.0, "z": 0.0},
    "radius_m": 2.0,
    "labels": ["person", "door"]
  }
}
```

### Record an observation
```json
{
  "type": "world.observe",
  "payload": {
    "source": "vision.detector",
    "objects": [
      {
        "id": "door-east",
        "label": "door",
        "category": "structure",
        "frame": "map",
        "position": {"x": 5.0, "y": 0.5, "z": 0.0},
        "confidence": 0.81,
        "tags": ["entry"]
      }
    ]
  }
}
```

## Controller integration

The CERBERUS controller can call this directly for:
- live detections panel
- semantic map overlays
- operator bookmarks
- editable targets

## Why it is low-hanging fruit

This plugin does not require full SLAM or advanced robotics to add real value.
It immediately improves:
- AI/Human interaction
- mission planning
- target selection
- semantic environment awareness

It is also the foundation for future:
- follow-person behavior
- docking behavior
- hazard avoidance
- room/object memory
