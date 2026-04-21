from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_replay_load_and_step():
    with TestClient(app) as client:
        jsonl = '{"timestamp":1,"type":"operator_text","payload":{"text":"hello"}}\n{"timestamp":2,"type":"goal_canceled","payload":{"goal_id":"g1"}}'
        loaded = client.post("/sweetie/replay/load", json={"jsonl": jsonl})
        assert loaded.status_code == 200
        assert loaded.json()["is_loaded"] is True
        assert loaded.json()["event_count"] == 2

        stepped = client.post("/sweetie/replay/step")
        assert stepped.status_code == 200
        data = stepped.json()
        assert data["event"]["type"] == "operator_text"
        assert data["replay"]["cursor"] == 1


def test_replay_clear_resets_state():
    with TestClient(app) as client:
        client.post("/sweetie/replay/load", json={"jsonl": '{"timestamp":1,"type":"x","payload":{}}'})
        cleared = client.post("/sweetie/replay/clear")
        assert cleared.status_code == 200
        data = cleared.json()
        assert data["is_loaded"] is False
        assert data["event_count"] == 0
