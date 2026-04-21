import requests

base = "http://localhost:7000"

payload = {
    "type": "behavior.process_intent",
    "payload": {
        "intent": "engage_operator",
        "context": {
            "target_id": "person-001",
            "is_operator": True,
            "battery": 0.76
        }
    }
}

print(requests.post(f"{base}/execute", json=payload, timeout=15).json())
