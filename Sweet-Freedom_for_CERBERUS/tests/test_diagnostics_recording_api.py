from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_diagnostics_route_returns_summary():
    with TestClient(app) as client:
        response = client.get("/sweetie/diagnostics")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "armed" in data["summary"]


def test_recording_export_contains_jsonl_lines():
    with TestClient(app) as client:
        client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        response = client.get("/sweetie/recording/export")
        assert response.status_code == 200
        body = response.text.strip()
        assert body
        assert '"type": "operator_text"' in body or '"type":"operator_text"' in body


def test_recording_clear_resets_event_count():
    with TestClient(app) as client:
        client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        response = client.post("/sweetie/recording/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["cleared"] is True
        assert data["recording"]["event_count"] == 0
