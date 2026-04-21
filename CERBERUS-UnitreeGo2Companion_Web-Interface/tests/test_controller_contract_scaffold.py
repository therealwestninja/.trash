from fastapi.testclient import TestClient

from backend.controller_contract_app import app


def test_state_contract_shape():
    with TestClient(app) as client:
        response = client.get('/state')
        assert response.status_code == 200
        data = response.json()
        assert data['hardware']['mode'] in {'real', 'simulation'}
        assert data['robot']['platform'] == 'unitree_go2'
        assert 'command_policy' in data
        assert 'telemetry' in data


def test_execute_ack_and_estop_restriction():
    with TestClient(app) as client:
        accepted = client.post('/execute', json={'category': 'motion', 'name': 'move', 'payload': {'vx': 0.2}})
        assert accepted.status_code == 200
        assert accepted.json()['status'] == 'accepted'

        estop = client.post('/safety/estop')
        assert estop.status_code == 200

        restricted = client.post('/execute', json={'category': 'motion', 'name': 'move', 'payload': {'vx': 0.2}})
        assert restricted.status_code == 200
        assert restricted.json()['status'] == 'rejected'
        assert restricted.json()['reason'] == 'category_not_allowed'
