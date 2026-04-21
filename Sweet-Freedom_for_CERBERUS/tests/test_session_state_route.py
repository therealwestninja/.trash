from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_session_state_route_reports_inactive_then_active():
    with TestClient(app) as client:
        inactive = client.get("/sweetie/session/state")
        assert inactive.status_code == 200
        assert inactive.json()["active"] is False

        acquired = client.post("/sweetie/session/acquire", json={"owner": "ui"})
        assert acquired.status_code == 200

        active = client.get("/sweetie/session/state")
        assert active.status_code == 200
        payload = active.json()
        assert payload["active"] is True
        assert payload["lease"]["owner"] == "ui"
