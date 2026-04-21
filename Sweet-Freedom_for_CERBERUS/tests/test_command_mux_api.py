from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_quick_action_can_be_blocked_by_locked_ui_source():
    with TestClient(app) as client:
        locked = client.post("/sweetie/control/lock", json={"source": "ui"})
        assert locked.status_code == 200

        response = client.post("/sweetie/action/quick", json={"action": "move_forward"})
        assert response.status_code == 200
        data = response.json()
        assert data["goal_result"]["status"] == "blocked"
        assert data["goal_result"]["code"] in {"source_blocked", "blocked"}

        unlocked = client.post("/sweetie/control/unlock", json={"source": "ui"})
        assert unlocked.status_code == 200


def test_runtime_state_exposes_command_mux():
    with TestClient(app) as client:
        response = client.get("/sweetie/runtime_full_state")
        assert response.status_code == 200
        data = response.json()
        assert "command_mux" in data
        assert "active_source" in data["command_mux"]
