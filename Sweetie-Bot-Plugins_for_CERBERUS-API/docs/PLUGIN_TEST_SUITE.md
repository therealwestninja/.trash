# Plugin test suite

This repository now includes a root-level pytest harness focused on Sweetie plugin contract mapping, endpoint discovery, functional smoke coverage, concurrency stress, fuzzing, and basic security regression checks.

## What it covers

- **Manifest validation**
  - Verifies every `plugins/*/plugin.yaml` file is readable and advertises at least one capability.
  - Confirms plugin names are unique.
  - Checks that declared entrypoints match live FastAPI routes when an app is present.

- **Inpoints / exitpoints / calls / commands mapping**
  - `scripts/map_plugin_contracts.py` walks the plugin tree and emits a JSON report of:
    - manifest metadata
    - declared capabilities
    - discovered HTTP routes
    - action strings seen in code comparisons
  - This is meant to make plugin command surfaces auditable before wiring them into the controller/runtime stack.

- **Functional smoke tests**
  - Health checks for every FastAPI plugin.
  - Execute-path probes for every plugin.
  - Representative valid command payloads for each plugin family.
  - Unknown-action and malformed-request handling.

- **Concurrency / race-condition pressure**
  - Parallel request floods against the most stateful plugins:
    - event bus
    - memory alaya
    - world model
    - payload bus
  - A dedicated publish/subscribe/poll parallel scenario for the event bus.

- **Security / fuzzing**
  - Common abuse strings including traversal, script injection, and oversized string probes.
  - Hypothesis-driven JSON fuzzing to ensure handlers reject bad inputs cleanly instead of crashing.

- **Performance guardrails**
  - Health endpoint latency budget.
  - Small execute-call batch timing budget for locally-computable plugins.

## Running the suite

Install the dev dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run everything:

```bash
pytest
```

Run only one category:

```bash
pytest -m smoke
pytest -m contract
pytest -m security
pytest -m concurrency
pytest -m performance
```

Generate the contract map report:

```bash
python scripts/map_plugin_contracts.py > plugin-contract-map.json
```

## Notes

- Some plugins are simple pass-through stubs. The suite still verifies that they do not crash and that their public interfaces remain stable.
- Plugins with external HTTP dependencies are isolated in tests with local test doubles so the suite can run offline and deterministically.
- Python services are not the place where classic native memory corruption is most likely, but the fuzz and abuse tests are still useful for surfacing parser crashes, unbounded payload handling, serialization blowups, and exception leaks.

## Avoiding bottlenecks and timeout stalls

The suite now supports a staged runner that writes results to disk instead of relying on long inline console logs. This keeps large runs readable and prevents one deep fuzz case from hiding the rest of the findings.

### Recommended staged run

```bash
python scripts/run_plugin_test_suite.py
```

This runner will:
- execute a fast/core pytest pass first
- write raw stdout/stderr logs to `test-results/`
- write a machine-readable JSON summary to `test-results/plugin-test-report.json`
- write a human-readable Markdown summary to `test-results/plugin-test-report.md`
- run the deep fuzz case separately, one plugin at a time
- enforce a per-plugin subprocess timeout for fuzzing so one bad case cannot stall the entire suite

### Useful environment controls

```bash
SWEETIE_FUZZ_EXAMPLES=6 python scripts/run_plugin_test_suite.py
SWEETIE_PLUGIN_FILTER=sweetie-plugin-event-bus python scripts/run_plugin_test_suite.py
SWEETIE_FUZZ_TIMEOUT_SECONDS=30 python scripts/run_plugin_test_suite.py
```

Supported knobs:
- `SWEETIE_PLUGIN_FILTER`: comma-separated plugin names to test
- `SWEETIE_FAST_FUZZ_EXAMPLES`: Hypothesis example count for the always-on quick fuzz test
- `SWEETIE_FUZZ_EXAMPLES`: Hypothesis example count for the deep fuzz test
- `SWEETIE_FUZZ_TIMEOUT_SECONDS`: per-plugin timeout for the isolated fuzz subprocess
- `SWEETIE_MAX_PROBE_LENGTH`: maximum oversized-string abuse payload length
- `SWEETIE_FUZZ_MAX_KEYS`: maximum number of keys in generated fuzz payloads
- `SWEETIE_FUZZ_MAX_TEXT`: maximum generated text length inside fuzz payloads

### Fast CI / deep nightly split

For pull requests and quick local checks, prefer:

```bash
pytest -m "not slow"
```

For a deeper pass, use the staged runner above or run only the slow fuzz test against targeted plugins.
