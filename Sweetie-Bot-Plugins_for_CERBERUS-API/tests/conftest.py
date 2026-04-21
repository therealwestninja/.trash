from __future__ import annotations

import importlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
import os
from typing import Any, Dict, Iterator

import pytest
import yaml
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"


@dataclass(frozen=True)
class PluginInfo:
    name: str
    path: Path
    manifest: Dict[str, Any]
    main_file: Path | None

    @property
    def capabilities(self) -> list[str]:
        return list(self.manifest.get("capabilities", []))

    @property
    def entrypoints(self) -> dict[str, str]:
        entrypoints = dict(self.manifest.get("entrypoints", {}))
        if "health" not in entrypoints and self.manifest.get("healthcheck"):
            entrypoints["health"] = self.manifest["healthcheck"]
        return entrypoints


def discover_plugins() -> list[PluginInfo]:
    plugins: list[PluginInfo] = []
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or not plugin_dir.name.startswith("sweetie-plugin-"):
            continue
        manifest_path = plugin_dir / "plugin.yaml"
        if not manifest_path.exists():
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        main_file = plugin_dir / "app" / "main.py"
        plugins.append(
            PluginInfo(
                name=str(manifest.get("name") or plugin_dir.name),
                path=plugin_dir,
                manifest=manifest,
                main_file=main_file if main_file.exists() else None,
            )
        )
    return plugins


ALL_PLUGINS = discover_plugins()
PLUGIN_BY_NAME = {plugin.name: plugin for plugin in ALL_PLUGINS}


def _selected_plugin_names() -> set[str] | None:
    raw = os.environ.get("SWEETIE_PLUGIN_FILTER", "").strip()
    if not raw:
        return None
    return {part.strip() for part in raw.split(",") if part.strip()}


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    selected = _selected_plugin_names()
    if not selected:
        return

    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        callspec = getattr(item, "callspec", None)
        plugin = None
        if callspec is not None:
            plugin = callspec.params.get("plugin")
        if plugin is None:
            kept.append(item)
            continue
        if getattr(plugin, "name", None) in selected:
            kept.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "plugin" in metafunc.fixturenames:
        metafunc.parametrize("plugin", ALL_PLUGINS, ids=[p.name for p in ALL_PLUGINS])


def _clear_plugin_modules() -> None:
    to_delete = [name for name in sys.modules if name == "app" or name.startswith("app.") or name.startswith("sweetie_plugin_sdk")]
    for name in to_delete:
        sys.modules.pop(name, None)
    importlib.invalidate_caches()


def load_plugin_app(plugin: PluginInfo):
    if not plugin.main_file:
        raise FileNotFoundError(f"No app/main.py found for {plugin.name}")

    _clear_plugin_modules()
    sys.path.insert(0, str(plugin.path))
    try:
        module = importlib.import_module("app.main")
        app = getattr(module, "app", None)
        if app is None:
            raise AttributeError(f"{plugin.name} main.py does not expose app")
        return app
    finally:
        try:
            sys.path.remove(str(plugin.path))
        except ValueError:
            pass


@pytest.fixture()
def plugin_client_factory(monkeypatch: pytest.MonkeyPatch):
    clients: list[TestClient] = []

    def factory(plugin: PluginInfo) -> TestClient:
        app = load_plugin_app(plugin)
        _apply_test_doubles(plugin, monkeypatch)
        client = TestClient(app)
        clients.append(client)
        return client

    yield factory

    for client in clients:
        client.close()
    _clear_plugin_modules()


def _apply_test_doubles(plugin: PluginInfo, monkeypatch: pytest.MonkeyPatch) -> None:
    routes_module = sys.modules.get("app.routes")
    if routes_module is None:
        return

    if plugin.name == "sweetie-plugin-cognitive-core":
        async def fake_call_execute(_url: str, payload: Dict[str, Any]):
            return {"ok": True, "echo": payload}
        monkeypatch.setattr(routes_module, "call_execute", fake_call_execute, raising=True)

    if plugin.name == "sweetie-plugin-runtime-orchestrator":
        async def fake_call_execute(_url: str, payload: Dict[str, Any]):
            action = payload.get("type")
            if action == "world.get_object":
                return {
                    "ok": True,
                    "data": {
                        "result": {
                            "object": {
                                "id": payload["payload"]["id"],
                                "label": "person",
                                "frame": "map",
                                "position": {"x": 1.0, "y": 2.0, "z": 0.0},
                            }
                        }
                    },
                }
            if action == "nav.goal":
                return {"ok": True, "data": {"accepted": True, "goal_id": "goal-test"}}
            if action == "mission.start":
                return {"ok": True, "data": {"started": True, "mission_id": "mission-test"}}
            if action == "sim.episode_start":
                return {"ok": True, "data": {"episode": {"episode_id": "episode-test"}}}
            if action == "sim.step":
                return {"ok": True, "data": {"step": {"done": payload.get("payload", {}).get("done", False), "index": 1}}}
            if action == "sim.episode_end":
                return {"ok": True, "data": {"episode": {"episode_id": payload.get("payload", {}).get("episode_id", "episode-test")}}}
            if action == "sim.replay_create":
                return {"ok": True, "data": {"replay": {"replay_id": "replay-test"}}}
            return {"ok": True, "data": {"echo": payload}}

        monkeypatch.setattr(routes_module, "call_execute", fake_call_execute, raising=True)


@pytest.fixture(scope="session")
def all_plugins() -> list[PluginInfo]:
    return ALL_PLUGINS
