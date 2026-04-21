import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={"type":"docking.set_dock","payload":{"dock_name":"charging_dock","position":{"x":2.1,"y":-0.5}}},
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={"type":"docking.seek_dock","payload":{"battery":0.16,"current_position":{"x":0.0,"y":0.0}}},
    timeout=15,
).json())
