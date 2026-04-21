from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_runtime_state_exposes_lifecycle():
    with TestClient(app) as client:
        response = client.get("/sweetie/runtime_full_state")
        assert response.status_code == 200
        data = response.json()
        assert "lifecycle" in data
        assert "phase" in data["lifecycle"]


def test_lifecycle_recover_route_returns_ready_state():
    with TestClient(app) as client:
        client.post("/sweetie/safety/estop")
        response = client.post("/sweetie/lifecycle/recover")
        assert response.status_code == 200
        data = response.json()
        assert data["lifecycle"]["phase"] == "ready"
