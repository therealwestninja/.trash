from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_runtime_state_still_has_expected_composed_sections():
    with TestClient(app) as client:
        response = client.get("/sweetie/runtime_full_state")
        assert response.status_code == 200
        data = response.json()
        assert "telemetry" in data
        assert "diagnostics" in data
        assert "lifecycle" in data
        assert "recording" in data


def test_operator_text_still_records_history_after_refactor():
    with TestClient(app) as client:
        response = client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["command_history"]) >= 1
        assert data["command_history"][0]["text"] == "hello sweetie"
