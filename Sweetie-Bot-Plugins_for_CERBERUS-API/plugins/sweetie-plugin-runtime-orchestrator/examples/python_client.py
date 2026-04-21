import requests

base = "http://localhost:7000"

payload = {
    "type": "runtime.patrol_mission",
    "payload": {
        "waypoints": [
            {"x": 0.0, "y": 0.0},
            {"x": 2.0, "y": 0.0},
            {"x": 2.0, "y": 2.0},
        ],
        "loop": True,
    }
}

resp = requests.post(f"{base}/execute", json=payload, timeout=20)
print(resp.status_code)
print(resp.json())
