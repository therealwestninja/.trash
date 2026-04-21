from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_operator_text_updates_runtime_state():
    with TestClient(app) as client:
        response = client.post("/sweetie/operator_text", json={"text": "hello sweetie"})
        assert response.status_code == 200
        data = response.json()
        assert data["current_action"]["action"] == "greet"
        assert data["last_action_result"]["status"] == "completed"
        assert data["expression"]["expression"] in {"calm", "happy", "curious", "guarded"}


def test_estop_blocks_move_action():
    with TestClient(app) as client:
        estop = client.post("/sweetie/safety/estop")
        assert estop.status_code == 200
        blocked = client.post("/sweetie/operator_text", json={"text": "move forward"})
        assert blocked.status_code == 200
        data = blocked.json()
        assert data["current_action"]["action"] == "move"
        assert data["last_action_result"]["status"] == "blocked"


def test_websocket_receives_runtime_state_and_heartbeat():
    with TestClient(app) as client:
        with client.websocket_connect("/sweetie/ws") as ws:
            first = ws.receive_json()
            assert first["type"] == "runtime_state"

            ws.send_text("ping")
            second = ws.receive_json()
            assert second["type"] == "heartbeat"
