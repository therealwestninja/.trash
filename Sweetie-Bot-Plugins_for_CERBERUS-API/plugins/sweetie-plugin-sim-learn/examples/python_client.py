import requests

base = "http://localhost:7000"

start = requests.post(
    f"{base}/execute",
    json={
        "type": "sim.episode_start",
        "payload": {
            "episode_name": "demo-episode",
            "scenario": "test-room",
            "metadata": {"operator": "dev"}
        },
    },
    timeout=15,
).json()

episode_id = start["data"]["episode"]["episode_id"]
print("Started:", episode_id)

requests.post(
    f"{base}/execute",
    json={
        "type": "sim.step",
        "payload": {
            "episode_id": episode_id,
            "observation": {"battery": 0.91, "person_seen": True},
            "action": {"type": "nav.goal", "payload": {"x": 1.0, "y": 0.5}},
            "reward": 0.25,
            "done": False,
            "notes": ["first step"],
        },
    },
    timeout=15,
)

end = requests.post(
    f"{base}/execute",
    json={
        "type": "sim.episode_end",
        "payload": {
            "episode_id": episode_id,
            "outcome": "success",
            "summary": {"distance_m": 1.12},
        },
    },
    timeout=15,
).json()

print(end)
