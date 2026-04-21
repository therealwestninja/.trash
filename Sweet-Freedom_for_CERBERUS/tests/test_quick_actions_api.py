from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_quick_action_route_executes_greet():
    with TestClient(app) as client:
        response = client.post("/sweetie/action/quick", json={"action": "greet"})
        assert response.status_code == 200
        data = response.json()
        assert data["current_action"]["action"] == "greet"
        assert "telemetry" in data
        assert "command_history" in data


def test_runtime_state_contains_simulation_telemetry():
    with TestClient(app) as client:
        client.post("/sweetie/action/quick", json={"action": "move_forward"})
        response = client.get("/sweetie/runtime_full_state")
        assert response.status_code == 200
        data = response.json()
        assert data["telemetry"]["motion_state"] in {"moving", "blocked", "idle", "stopped", "scanning", "estop"}
        assert isinstance(data["command_history"], list)
