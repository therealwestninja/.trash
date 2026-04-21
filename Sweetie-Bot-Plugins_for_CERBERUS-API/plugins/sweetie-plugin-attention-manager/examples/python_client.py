import requests

base = "http://localhost:7000"

payload = {
    "type": "attention.ingest_candidates",
    "payload": {
        "candidates": [
            {
                "target_id": "person-001",
                "label": "person",
                "confidence": 0.95,
                "tags": ["operator"],
                "distance_m": 1.0,
                "novelty": 0.2,
                "salience": 0.95
            },
            {
                "target_id": "object-100",
                "label": "toy",
                "confidence": 0.88,
                "tags": ["novel"],
                "distance_m": 1.8,
                "novelty": 0.85,
                "salience": 0.55
            }
        ]
    }
}

print(requests.post(f"{base}/execute", json=payload, timeout=15).json())
print(requests.post(f"{base}/execute", json={"type":"attention.select_focus","payload":{}}, timeout=15).json())
