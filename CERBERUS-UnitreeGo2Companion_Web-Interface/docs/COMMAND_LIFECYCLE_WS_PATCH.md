# Command Lifecycle + WebSocket Tracking Patch

This patch upgrades the controller contract scaffold with ordered command lifecycle tracking and a stronger WebSocket transport.

## Added
- `backend/controller_contract/command_tracker.py`
- `GET /commands`
- `GET /commands/{command_id}`
- WebSocket `snapshot` envelope on connect
- replay buffer for recent envelopes
- periodic `telemetry` and `system_state` publishing

## Command lifecycle
Each accepted command now moves through:
- `queued`
- `running`
- `completed` or `failed`

Each transition emits a `command_update` envelope with:
- `id`
- `state`
- `sequence`
- `queue_depth`
- `active_command_id`
- `reason` when present
- `result` when present

## State additions
`GET /state` now includes `command_runtime` with:
- `queue_depth`
- `active_command_id`
- `total_commands_seen`
- `last_command_id`
- `worker_started`

## WebSocket behavior
Clients connecting to `/ws` receive:
1. a `snapshot` envelope with current state and recent commands
2. optional replay of recent envelopes
3. live `telemetry`, `system_state`, `command_update`, `fault`, `warning`, and `heartbeat`

Set `?replay=0` on the WebSocket URL to skip replay after the snapshot.
