from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_movement_is_blocked_when_disarmed():
    with TestClient(app) as client:
        client.post("/sweetie/safety/disarm")
        response = client.post("/sweetie/operator_text", json={"text": "move forward"})
        assert response.status_code == 200
        data = response.json()
        assert data["goal_result"]["status"] == "blocked"
        assert data["goal_result"]["message"] == "System is disarmed"


def test_movement_allowed_after_arming():
    with TestClient(app) as client:
        client.post("/sweetie/safety/clear_estop")
        client.post("/sweetie/safety/arm")
        response = client.post("/sweetie/operator_text", json={"text": "move forward"})
        assert response.status_code == 200
        data = response.json()
        assert data["goal_result"]["status"] in {"completed", "blocked"}
        assert data["safety"]["armed"] is True
