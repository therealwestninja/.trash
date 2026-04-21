import requests

base = "http://localhost:7000"

payload = {
    "type": "world.observe",
    "payload": {
        "source": "vision.detector",
        "objects": [
            {
                "id": "person-001",
                "label": "person",
                "category": "human",
                "frame": "map",
                "position": {"x": 1.25, "y": 2.75, "z": 0.0},
                "confidence": 0.93,
                "attributes": {"name": "operator"},
                "tags": ["operator", "human"]
            }
        ]
    }
}

resp = requests.post(f"{base}/execute", json=payload, timeout=15)
print(resp.status_code)
print(resp.json())
