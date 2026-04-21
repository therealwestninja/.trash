import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={
        "type": "learning.record_outcome",
        "payload": {
            "behavior": "follow_operator",
            "outcome": "success",
            "reward": 0.8,
            "tags": ["operator", "social"],
            "notes": ["operator stayed engaged"]
        }
    },
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={"type":"learning.get_profile","payload":{}},
    timeout=15,
).json())
