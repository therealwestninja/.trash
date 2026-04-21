# sweetie-plugin-payload-bus

A reusable payload and module registry for the Sweetie-Bot / CERBERUS plugin ecosystem.

This plugin standardizes the idea of **external payloads** and **service add-ons**:
- cameras
- microphones
- lidar
- thermal sensors
- docking modules
- vision services
- speech services
- external inference services
- third-party helper plugins

It is inspired by mature quadruped ecosystems that treat payloads and auxiliary services as first-class extensions.

## What problem it solves

Without a payload registry:
- every sensor or helper service is hardcoded
- controller integrations drift
- discovery is manual
- feature routing becomes brittle

With a payload bus:
- modules can self-register
- CERBERUS can discover capabilities dynamically
- controller can show available modules/services
- plugins can route requests by capability instead of fixed addresses

## Supported execute actions

- `payload.register`
- `payload.unregister`
- `payload.heartbeat`
- `payload.get`
- `payload.list`
- `payload.list_by_capability`
- `payload.route_request`
- `payload.status`

## Payload shape

```json
{
  "id": "front-camera",
  "name": "Front Camera",
  "kind": "camera",
  "version": "1.0.0",
  "base_url": "http://front-camera-plugin:7101",
  "health_url": "http://front-camera-plugin:7101/health",
  "capabilities": ["vision.detect", "vision.snapshot"],
  "metadata": {
    "position": "front",
    "resolution": "1920x1080"
  },
  "heartbeat_ttl_seconds": 300
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
docker build -t sweetie-plugin-payload-bus .
docker run --rm -p 7000:7000 --env-file .env.example sweetie-plugin-payload-bus
```

## Example: register a module

```bash
curl -X POST http://localhost:7000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payload.register",
    "payload": {
      "id": "front-camera",
      "name": "Front Camera",
      "kind": "camera",
      "version": "1.0.0",
      "base_url": "http://front-camera-plugin:7101",
      "health_url": "http://front-camera-plugin:7101/health",
      "capabilities": ["vision.detect", "vision.snapshot"],
      "metadata": {"position":"front"}
    }
  }'
```

## Example: route a request by capability

```json
{
  "type": "payload.route_request",
  "payload": {
    "capability": "vision.snapshot",
    "request": {
      "type": "vision.snapshot",
      "payload": {
        "camera": "front"
      }
    }
  }
}
```

This plugin currently returns the selected target and a normalized forwarding envelope.
That keeps the contract usable immediately, before enabling real proxying.

## Why it is low-hanging fruit

This adds a lot of platform value without deep robotics work:
- discoverable modules
- extensible controller UI
- dynamic feature routing
- less hardcoding
- easier third-party plugin support

## Future uses

This will become the foundation for:
- hot-pluggable perception modules
- optional AI services
- docking/charging subsystems
- swappable speech/TTS backends
- extra robot hardware integrations
