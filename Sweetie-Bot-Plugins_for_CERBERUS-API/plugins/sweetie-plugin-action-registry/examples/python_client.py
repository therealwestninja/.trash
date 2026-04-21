import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={
        "type": "action.register",
        "payload": {
            "action_name": "follow_operator",
            "description": "Follow a known operator target.",
            "handler_type": "plugin_execute",
            "target_plugin": "runtime-orchestrator",
            "target_action": "runtime.follow_object",
            "default_payload": {"object_id": "operator-001", "standoff_m": 0.75},
            "tags": ["follow", "operator"],
            "policy": {"safety_level": "normal"}
        }
    },
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={
        "type": "action.dispatch",
        "payload": {
            "action_name": "follow_operator",
            "payload_override": {"object_id": "person-001"}
        }
    },
    timeout=15,
).json())
