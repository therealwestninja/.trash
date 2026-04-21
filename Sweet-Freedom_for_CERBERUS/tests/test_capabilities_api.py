from fastapi.testclient import TestClient

from controller.app.main_v2 import app


def test_capabilities_route_returns_registry_snapshot():
    with TestClient(app) as client:
        response = client.get("/sweetie/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert isinstance(data["capabilities"], list)


def test_api_v1_capabilities_alias_works():
    with TestClient(app) as client:
        response = client.get("/api/v1/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data


def test_capability_detail_route_works():
    with TestClient(app) as client:
        response = client.get("/sweetie/capabilities/movement.basic")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "movement.basic"
