# API Integration

## Backend base URL

Default: `http://localhost:8080` — configurable in Settings → API URL.

## Authentication

All REST requests include `X-CERBERUS-Key: <key>` (set in auth modal).
WebSocket appends `?api_key=<key>` (browsers cannot set WS headers).

## REST endpoints used by the frontend

| Method | Path                      | Used by       | Purpose                    |
|--------|---------------------------|---------------|----------------------------|
| GET    | /state                    | ws.js         | Initial state snapshot     |
| GET    | /stats                    | metrics.js    | Engine Hz, uptime          |
| GET    | /health                   | metrics.js    | Health checks              |
| GET    | /anatomy                  | metrics.js    | Kinematics / joints        |
| GET    | /behavior                 | behaviors.js  | Cognitive engine status    |
| GET    | /plugins                  | behaviors.js  | Plugin roster              |
| GET    | /terrain                  | ws.js         | Initial terrain class      |
| GET    | /safety/events            | metrics.js    | Audit log                  |
| GET    | /session                  | ws.js         | Personality / stats        |
| GET    | /stair                    | (available)   | Stair plugin status        |
| GET    | /limb_loss                | (available)   | Limb loss status           |
| GET    | /payload                  | (available)   | Payload status             |
| POST   | /safety/estop             | cmd.js        | Emergency stop             |
| POST   | /safety/clear_estop       | cmd.js        | Clear estop (sim only)     |
| POST   | /motion/stand_up          | cmd.js        |                            |
| POST   | /motion/stand_down        | cmd.js        |                            |
| POST   | /motion/stop              | cmd.js        |                            |
| POST   | /motion/move              | cmd.js        | {vx, vy, vyaw}             |
| POST   | /motion/body_height       | cmd.js        | {height}                   |
| POST   | /motion/euler             | cmd.js        | {roll, pitch, yaw} radians |
| POST   | /motion/gait              | cmd.js        | {gait_id}                  |
| POST   | /motion/sport_mode        | cmd.js        | {mode}                     |
| POST   | /behavior/goal            | cmd.js        | {name, priority}           |
| POST   | /plugins/{name}/enable    | behaviors.js  |                            |
| POST   | /plugins/{name}/disable   | behaviors.js  |                            |

## WebSocket — inbound message types

| type       | Handler                  | Notes                              |
|------------|--------------------------|------------------------------------|
| state      | ws.js → telemetry.js     | 30 Hz robot state stream           |
| terrain    | ws.js → ui.js            | TerrainArbiter classification      |
| stair      | ws.js → plugin-status.js | StairClimber events                |
| payload    | ws.js → plugin-status.js | UndercarriagePayload events        |
| limb_loss  | ws.js → plugin-status.js | LimbLossRecovery events            |
| voice      | ws.js → log              | VoiceNLU transcript/intent         |
| error      | ws.js → log              | Backend command rejection          |
| ping       | ws.js (ignored)          | Server keep-alive                  |

## WebSocket — outbound command protocol

The backend's `_handle_ws_command()` accepts JSON frames for low-latency
control. Use `sendWsCmd(cmd, params)` from `ws.js`.

| cmd         | Params                     | Used by       |
|-------------|----------------------------|---------------|
| move        | {vx, vy, vyaw}             | joystick.js   |
| stop        | —                          | joystick.js   |
| estop       | —                          | available      |
| sport_mode  | {mode}                     | available      |
| body_height | {height}                   | available      |
| led         | {r, g, b}                  | available      |

Unknown commands return `{type: "error"}` — these appear in the operator log.


## Maintainer note
Controller-side Sweetie plugin endpoint wiring is currently summarized in `../UPDATE-NEEDED.md` and `./CHANGELOG.md` until a dedicated plugin integration guide is added.
