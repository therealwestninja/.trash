from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_operator_text_creates_goal_feedback_and_result():
    with TestClient(app) as client:
        response = client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        assert response.status_code == 200
        data = response.json()
        assert data["active_goal"]["action_type"] == "greet"
        assert data["last_feedback"]["status"] in {"accepted", "running", "completed", "blocked"}
        assert data["goal_result"]["status"] == "completed"


def test_session_acquire_checkin_release_cycle():
    with TestClient(app) as client:
        acquired = client.post("/sweetie/session/acquire", json={"owner": "ui"})
        assert acquired.status_code == 200
        lease_id = acquired.json()["lease_id"]

        checked = client.post("/sweetie/session/checkin", json={"lease_id": lease_id})
        assert checked.status_code == 200
        assert checked.json()["lease_id"] == lease_id

        released = client.post("/sweetie/session/release", json={"lease_id": lease_id})
        assert released.status_code == 200
        assert released.json()["released"] is True


def test_estop_blocks_goal_result():
    with TestClient(app) as client:
        client.post("/sweetie/safety/estop")
        response = client.post("/sweetie/operator_text", json={"text": "move forward"})
        assert response.status_code == 200
        data = response.json()
        assert data["goal_result"]["status"] == "blocked"
