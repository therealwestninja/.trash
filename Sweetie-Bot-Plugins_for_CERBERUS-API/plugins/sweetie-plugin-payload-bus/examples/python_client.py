import requests

base = "http://localhost:7000"

register_payload = {
    "type": "payload.register",
    "payload": {
        "id": "front-camera",
        "name": "Front Camera",
        "kind": "camera",
        "version": "1.0.0",
        "base_url": "http://front-camera-plugin:7101",
        "health_url": "http://front-camera-plugin:7101/health",
        "capabilities": ["vision.detect", "vision.snapshot"],
        "metadata": {"position": "front"}
    }
}

print(requests.post(f"{base}/execute", json=register_payload, timeout=15).json())

route_request = {
    "type": "payload.route_request",
    "payload": {
        "capability": "vision.snapshot",
        "request": {
            "type": "vision.snapshot",
            "payload": {"camera": "front"}
        }
    }
}

print(requests.post(f"{base}/execute", json=route_request, timeout=15).json())
