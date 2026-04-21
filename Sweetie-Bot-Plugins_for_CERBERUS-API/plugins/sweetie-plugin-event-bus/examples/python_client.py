import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={
        "type": "event.subscribe",
        "payload": {
            "subscriber_id": "demo-subscriber",
            "topics": ["vision.*", "world.*"]
        }
    },
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={
        "type": "event.publish",
        "payload": {
            "topic": "vision.person_detected",
            "source": "vision.detector",
            "payload": {"id": "person-001", "confidence": 0.93},
            "tags": ["person", "operator"]
        }
    },
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={
        "type": "event.poll",
        "payload": {"subscriber_id": "demo-subscriber", "limit": 10}
    },
    timeout=15,
).json())
