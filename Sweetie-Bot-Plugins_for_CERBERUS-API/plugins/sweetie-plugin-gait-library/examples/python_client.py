import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={"type": "gait.set_active", "payload": {"profile": "equine", "gait": "tolt"}},
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={
        "type": "gait.adapt_command",
        "payload": {
            "command": {
                "type": "robot.command",
                "payload": {
                    "action": "move",
                    "direction": "forward",
                    "speed_mps": 0.9,
                    "duration_s": 2.5,
                },
            }
        },
    },
    timeout=15,
).json())
