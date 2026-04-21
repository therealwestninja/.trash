from __future__ import annotations

import pytest

from tests.plugin_expectations import MALFORMED_CASE, UNKNOWN_ACTION_CASE, VALID_EXECUTE_CASES


@pytest.mark.smoke
def test_valid_execute_cases_do_not_500(plugin, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    for case in VALID_EXECUTE_CASES.get(plugin.name, []):
        response = client.post(plugin.entrypoints.get("execute", "/execute"), json=case)
        assert response.status_code < 500, f"{plugin.name} failed case {case['type']}: {response.text}"


@pytest.mark.smoke
def test_unknown_action_does_not_crash(plugin, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    response = client.post(plugin.entrypoints.get("execute", "/execute"), json=UNKNOWN_ACTION_CASE)
    assert response.status_code < 500


@pytest.mark.smoke
def test_malformed_request_is_rejected_without_500(plugin, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    response = client.post(plugin.entrypoints.get("execute", "/execute"), json=MALFORMED_CASE)
    assert response.status_code in {200, 400, 422}
