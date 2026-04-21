import requests

base = "http://localhost:7000"

event = {
    "type": "cognition.perceive_event",
    "payload": {
        "event": {
            "topic": "vision.person_detected",
            "source": "perception-core",
            "payload": {
                "track_id": "person-001",
                "label": "person",
                "confidence": 0.95,
                "position": {"x": 1.1, "y": 0.2},
                "tags": ["operator"]
            }
        }
    }
}

print(requests.post(f"{base}/execute", json=event, timeout=20).json())
print(requests.post(f"{base}/execute", json={"type":"cognition.get_state","payload":{}}, timeout=20).json())
print(requests.post(f"{base}/execute", json={"type":"cognition.choose_action","payload":{"context":{"battery":0.81}}}, timeout=20).json())
