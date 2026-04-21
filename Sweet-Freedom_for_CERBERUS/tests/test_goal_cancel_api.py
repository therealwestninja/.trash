from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_goal_can_be_canceled():
    with TestClient(app) as client:
        created = client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        assert created.status_code == 200
        goal_id = created.json()["active_goal"]["goal_id"]

        canceled = client.post("/sweetie/action/cancel", json={"goal_id": goal_id, "requested_by": "ui"})
        assert canceled.status_code == 200
        data = canceled.json()
        assert data["goal_result"]["status"] == "canceled"
        assert data["last_feedback"]["status"] == "canceled"
