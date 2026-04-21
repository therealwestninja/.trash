import time

import pytest
from fastapi.testclient import TestClient

from backend.controller_contract.event_bus import EventBus
from backend.controller_contract.models import ExecuteCommandRequest
from backend.controller_contract_app import app


def test_command_lifecycle_http_endpoints():
    with TestClient(app) as client:
        response = client.post('/execute', json={
            'category': 'motion',
            'name': 'move',
            'payload': {'vx': 1.0},
            'client_api_version': '1.2.0',
        })
        assert response.status_code == 200
        body = response.json()
        assert body['status'] == 'accepted'
        command_id = body['id']

        for _ in range(30):
            details = client.get(f'/commands/{command_id}')
            assert details.status_code == 200
            if details.json()['state'] == 'completed':
                break
            time.sleep(0.01)

        details = client.get(f'/commands/{command_id}')
        assert details.json()['state'] == 'completed'
        history = client.get('/commands').json()
        assert history['items'][0]['id'] == command_id
        assert history['items'][0]['state'] == 'completed'


@pytest.mark.asyncio
async def test_event_bus_snapshot_and_replay():
    bus = EventBus(replay_limit=5)

    class FakeWebSocket:
        def __init__(self):
            self.messages = []
        async def send_text(self, value):
            self.messages.append(value)
        async def accept(self):
            return None

    ws = FakeWebSocket()
    await bus.register_client(ws)
    await bus.publish('command_update', {'id': 'cmd_1'})
    await bus.send_snapshot(ws, {'hello': 'world'})
    await bus.replay_recent(ws, limit=1)
    assert any('snapshot' in msg for msg in ws.messages)
    assert any('command_update' in msg for msg in ws.messages)
