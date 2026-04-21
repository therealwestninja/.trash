from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_api_v1_health_alias_works():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_api_v1_operator_text_alias_works():
    with TestClient(app) as client:
        response = client.post("/api/v1/operator/text", json={"text": "hello sweetie"})
        assert response.status_code == 200
        data = response.json()
        assert "active_goal" in data


def test_api_v1_session_state_alias_works():
    with TestClient(app) as client:
        response = client.get("/api/v1/session/state")
        assert response.status_code == 200
        data = response.json()
        assert "active" in data
