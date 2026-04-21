import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={"type": "navigation.set_position", "payload": {"position": {"x": 0.0, "y": 0.0}}},
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={"type": "navigation.plan_to_point", "payload": {"goal": {"x": 2.0, "y": 1.0}}},
    timeout=15,
).json())
