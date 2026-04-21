from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.conftest import PLUGINS_DIR, PluginInfo


@pytest.mark.contract
@pytest.mark.parametrize("manifest_path", sorted(PLUGINS_DIR.glob("*/plugin.yaml")), ids=lambda p: p.parent.name)
def test_plugin_manifest_is_valid_yaml(manifest_path: Path):
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    assert manifest.get("name")
    assert manifest.get("version") is not None
    assert isinstance(manifest.get("capabilities"), list)
    assert manifest["capabilities"], f"{manifest_path.parent.name} should advertise at least one capability"


@pytest.mark.contract
def test_discovered_plugins_have_unique_names(all_plugins: list[PluginInfo]):
    names = [plugin.name for plugin in all_plugins]
    assert len(names) == len(set(names))


@pytest.mark.contract
def test_every_plugin_has_minimum_layout(plugin: PluginInfo):
    assert (plugin.path / "plugin.yaml").exists()
    assert (plugin.path / "requirements.txt").exists()
    assert (plugin.path / "README.md").exists() or plugin.main_file is not None


@pytest.mark.contract
def test_health_endpoint_declared_or_implemented(plugin: PluginInfo, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    response = client.get(plugin.entrypoints.get("health", "/health"))
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"


@pytest.mark.contract
def test_execute_endpoint_exists_for_app_plugins(plugin: PluginInfo, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    response = client.post(plugin.entrypoints.get("execute", "/execute"), json={"type": "contract.probe", "payload": {}})
    assert response.status_code < 500


@pytest.mark.contract
def test_declared_entrypoints_are_present_in_openapi_when_available(plugin: PluginInfo, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    paths = openapi.json().get("paths", {})
    for _name, route in plugin.entrypoints.items():
        assert route in paths or route == "/docs", f"{plugin.name} missing declared route {route} in OpenAPI"
