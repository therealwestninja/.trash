import requests

base = "http://localhost:7000"

print(requests.post(
    f"{base}/execute",
    json={
        "type": "autonomy.report_context",
        "payload": {
            "battery": 0.16,
            "safety_blocked": False,
            "operator_visible": False,
            "social_target_visible": False,
            "routine_triggered": ["patrol_area"],
            "dock_known": True,
            "charging": False
        }
    },
    timeout=15,
).json())

print(requests.post(
    f"{base}/execute",
    json={"type":"autonomy.choose_goal","payload":{}},
    timeout=15,
).json())
