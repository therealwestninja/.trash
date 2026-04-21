import requests

base = "http://localhost:7000"

requests.post(f"{base}/execute", json={
    "type": "consolidator.ingest_episode",
    "payload": {
        "text": "Followed the operator from the hallway to the charging dock.",
        "tags": ["operator", "charging_dock", "hallway"],
        "salience": 0.88
    }
}, timeout=15)

requests.post(f"{base}/execute", json={
    "type": "consolidator.ingest_location",
    "payload": {
        "name": "charging_dock",
        "position": {"x": 2.1, "y": -0.5},
        "confidence": 0.93
    }
}, timeout=15)

requests.post(f"{base}/execute", json={
    "type": "consolidator.ingest_behavior_outcome",
    "payload": {
        "behavior": "follow_operator",
        "reward": 0.82,
        "outcome": "success",
        "tags": ["operator", "social"]
    }
}, timeout=15)

print(requests.post(f"{base}/execute", json={
    "type": "consolidator.consolidate",
    "payload": {}
}, timeout=15).json())
