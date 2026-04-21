from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_session_release_response_is_typed_shape():
    with TestClient(app) as client:
        acquired = client.post("/sweetie/session/acquire", json={"owner": "ui"})
        lease_id = acquired.json()["lease_id"]

        released = client.post("/sweetie/session/release", json={"lease_id": lease_id})
        assert released.status_code == 200
        data = released.json()
        assert data["ok"] is True
        assert data["message"] == "session released"


def test_recording_clear_response_is_typed_shape():
    with TestClient(app) as client:
        cleared = client.post("/sweetie/recording/clear")
        assert cleared.status_code == 200
        data = cleared.json()
        assert data["ok"] is True
        assert data["message"] == "recording cleared"


def test_websocket_uses_normalized_event_envelope():
    with TestClient(app) as client:
        with client.websocket_connect("/sweetie/ws") as ws:
            first = ws.receive_json()
            assert first["type"] == "runtime_state"
            assert "data" in first
