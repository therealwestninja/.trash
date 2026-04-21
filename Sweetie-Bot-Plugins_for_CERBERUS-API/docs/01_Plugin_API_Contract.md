# Plugin API Contract

## Goal
All Sweetie-Bot plugins should look and behave the same at the HTTP contract level.

## Required Endpoints

### `POST /execute`
Primary action endpoint.

### `GET /health`
Liveness probe.

### `GET /manifest`
Returns static plugin metadata.

### `GET /status` *(recommended)*
Returns runtime health, dependency visibility, request counters, and current mode.

## Standard Request Envelope
The controller should send a single execute shape to all plugins.

```json
{
  "request_id": "7c4a4c13-8208-4ec9-a06a-c0f2e8f8d901",
  "timestamp": "2026-03-30T22:00:00Z",
  "source": "controller",
  "plugin": "sweetie-plugin-mood",
  "action": "mood.update",
  "session": {
    "session_id": "sess_001",
    "conversation_id": "conv_001",
    "actor_id": "sweetie-bot",
    "environment_id": "lab-alpha"
  },
  "context": {
    "trace_id": "trace_001",
    "user_id": "operator_001",
    "priority": "normal",
    "mode": "interactive"
  },
  "state": {},
  "input": {},
  "policy": {
    "dry_run": false,
    "timeout_ms": 1200,
    "safe_mode": true
  }
}
```

## Standard Response Envelope

```json
{
  "ok": true,
  "request_id": "7c4a4c13-8208-4ec9-a06a-c0f2e8f8d901",
  "plugin": "sweetie-plugin-mood",
  "action": "mood.update",
  "version": "1.0.0",
  "result": {},
  "state_patch": {},
  "events": [],
  "commands": [],
  "warnings": [],
  "errors": []
}
```

## Action Naming
Use `domain.verb` naming:
- `mission.plan`
- `mood.update`
- `social.rank_targets`
- `attention.select_focus`
- `behavior.select`
- `expression.compose`
- `action.dispatch`
- `runtime.execute`

## Event Naming
Use `domain.past_tense`:
- `mood.changed`
- `mission.updated`
- `focus.selected`
- `runtime.stopped`

## Command Naming
Commands should represent high-level intent rather than hardware-specific implementation.
Examples:
- `expression.perform`
- `voice.speak`
- `runtime.execute_action`
- `motion.stop`

## Error Contract
Errors should be structured and machine-readable.
Recommended codes:
- `INVALID_ACTION`
- `INVALID_REQUEST`
- `INVALID_STATE`
- `DEPENDENCY_UNAVAILABLE`
- `PLUGIN_TIMEOUT`
- `SAFETY_BLOCKED`
- `POLICY_DENIED`
- `NOT_IMPLEMENTED`

## Manifest Requirements
Every plugin should ship a `plugin.yaml` file declaring:
- name
- version
- api version
- description
- capabilities
- entrypoints
- dependencies
- state ownership
- events published and subscribed to
- safety behavior

## Compatibility Rule
A plugin should not expose a unique request format unless there is a very strong reason. The point of the standard contract is to keep the ecosystem replaceable and testable.
