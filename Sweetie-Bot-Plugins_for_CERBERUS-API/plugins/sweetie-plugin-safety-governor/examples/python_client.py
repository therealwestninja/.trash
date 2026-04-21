import requests

base = "http://localhost:7000"

payload = {
    "type": "safety.evaluate_action",
    "payload": {
        "action": {
            "type": "runtime.follow_object",
            "payload": {
                "object_id": "person-001",
                "speed_mps": 1.6,
                "target_distance_m": 0.5,
                "position": {"x": 1.5, "y": 2.0}
            }
        },
        "context": {
            "battery": 0.18,
            "nearest_human_distance_m": 0.55
        }
    }
}

print(requests.post(f"{base}/execute", json=payload, timeout=15).json())
