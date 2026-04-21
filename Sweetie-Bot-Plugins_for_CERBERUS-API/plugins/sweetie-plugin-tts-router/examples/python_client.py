import requests

base = "http://localhost:7000"

payload = {
    "type": "tts.speak",
    "payload": {
        "text": "Ooo! There you are! I'll come with you!",
        "tone": "bright_cheerful",
        "emotion": "excited"
    }
}

print(requests.post(f"{base}/execute", json=payload, timeout=15).json())
