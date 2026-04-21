# sweetie-plugin-unitree-compat

A self-contained compatibility plugin that translates stable Sweetie/CERBERUS controller actions into Unitree-style high-level robot commands.

## What it does
- normalizes `stand`, `sit`, `stop`, `walk`, `strafe`, and `turn`
- supports posture presets and motion presets
- executes sequences of robot commands
- optionally forwards translated commands to the CERBERUS API

## Quick start

### Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7101
```

### Run with Docker
```bash
docker build -t sweetie-plugin-unitree-compat .
docker run --rm -p 7101:7101 --env-file .env.example sweetie-plugin-unitree-compat
```

## Endpoints
- `GET /health`
- `GET /manifest`
- `POST /execute`
- `POST /translate`

## Execute contract
```json
{
  "type": "robot.command",
  "payload": {
    "action": "walk",
    "direction": "forward",
    "speed": 0.4,
    "duration": 2.0
  },
  "context": {
    "forward_to_cerberus": false
  }
}
```

## Example: translate only
```bash
curl -X POST http://localhost:7101/translate   -H 'Content-Type: application/json'   -d '{"action":"walk","direction":"forward","speed":0.3}'
```

## Example: from JavaScript
```js
const res = await fetch("http://localhost:7101/execute", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    type: "robot.sequence",
    payload: {
      commands: [
        { action: "stand" },
        { action: "walk", direction: "forward", speed: 0.35, duration: 1.5 },
        { action: "turn", direction: "left", speed: 0.25, duration: 1.0 },
        { action: "sit" }
      ]
    }
  })
});
console.log(await res.json());
```

## Example: from Python using the bundled SDK
```python
from sweetie_plugin_sdk.client import SweetiePluginClient
client = SweetiePluginClient("http://localhost:7101")
print(client.execute("robot.posture", {"preset": "greet"}))
```

## How CERBERUS can use this
The CERBERUS controller can call this plugin directly, or the CERBERUS API can proxy plugin actions to it. The plugin returns both the **normalized command** and the **translated backend command**, so CERBERUS can adopt the translation layer incrementally.

## Supported action types
- `robot.command`
- `robot.sequence`
- `robot.posture`
- `robot.motion_preset`

## Current presets
### Posture presets
- `greet`
- `crouch`
- `observe`
- `neutral`

### Motion presets
- `patrol_step`
- `sidestep_left`
- `sidestep_right`
- `turn_scan`
