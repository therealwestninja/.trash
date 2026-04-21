from __future__ import annotations

import time

import pytest

from tests.plugin_expectations import VALID_EXECUTE_CASES


FAST_PATH_PLUGINS = {
    "sweetie-plugin-action-registry",
    "sweetie-plugin-event-bus",
    "sweetie-plugin-gait-library",
    "sweetie-plugin-interaction-core",
    "sweetie-plugin-leg-odometry",
    "sweetie-plugin-memory-alaya",
    "sweetie-plugin-payload-bus",
    "sweetie-plugin-perception-core",
    "sweetie-plugin-safety-governor",
    "sweetie-plugin-sim-learn",
    "sweetie-plugin-unitree-compat",
    "sweetie-plugin-world-model",
}


@pytest.mark.performance
def test_health_endpoint_latency_budget(plugin, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    started = time.perf_counter()
    response = client.get(plugin.entrypoints.get("health", "/health"))
    duration = time.perf_counter() - started
    assert response.status_code == 200
    assert duration < 0.5, f"{plugin.name} health endpoint exceeded budget: {duration:.3f}s"


@pytest.mark.performance
def test_execute_smoke_batch_latency(plugin, plugin_client_factory):
    if plugin.main_file is None or plugin.name not in FAST_PATH_PLUGINS:
        pytest.skip("Latency budget only enforced for local, non-network plugins")
    client = plugin_client_factory(plugin)
    case = (VALID_EXECUTE_CASES.get(plugin.name) or [{"type": plugin.capabilities[0], "payload": {}}])[0]
    started = time.perf_counter()
    for _ in range(10):
        response = client.post(plugin.entrypoints.get("execute", "/execute"), json=case)
        assert response.status_code < 500
    duration = time.perf_counter() - started
    assert duration < 3.0, f"{plugin.name} 10-call batch exceeded budget: {duration:.3f}s"
