import requests

base = "http://localhost:7000"

payload = {
    "type": "nav.follow_waypoints",
    "payload": {
        "frame": "map",
        "waypoints": [
            {"x": 1.0, "y": 0.0},
            {"x": 2.5, "y": 1.0},
            {"x": 3.0, "y": 1.5}
        ]
    }
}

resp = requests.post(f"{base}/execute", json=payload, timeout=15)
print(resp.status_code)
print(resp.json())
