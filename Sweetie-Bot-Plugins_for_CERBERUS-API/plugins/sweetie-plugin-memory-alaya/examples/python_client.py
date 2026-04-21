import requests

base = "http://localhost:7000"

episode = requests.post(
    f"{base}/execute",
    json={
        "type": "memory.store_episode",
        "payload": {
            "text": "Saw the operator near the front door.",
            "tags": ["operator", "front_door"],
            "source": "vision",
            "salience": 0.8,
        },
    },
    timeout=15,
).json()

print(episode)

query = requests.post(
    f"{base}/execute",
    json={
        "type": "memory.query",
        "payload": {
            "text": "Where was the operator seen?",
            "limit": 5,
        },
    },
    timeout=15,
).json()

print(query)
