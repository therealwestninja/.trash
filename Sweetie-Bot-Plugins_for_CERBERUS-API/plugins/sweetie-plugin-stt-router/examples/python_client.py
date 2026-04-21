import requests

base = "http://localhost:7000"

payload = {
    "type": "stt.process_utterance",
    "payload": {
        "transcript": "Sweetie, follow me please.",
        "speaker_id": "operator-001"
    }
}

print(requests.post(f"{base}/execute", json=payload, timeout=15).json())
