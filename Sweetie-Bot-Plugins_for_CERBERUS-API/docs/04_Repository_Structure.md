# Repository Structure Recommendation

## Goal
Keep the repo predictable for both human contributors and automation.

## Recommended Root Layout
```text
Docs/
controller/
schemas/
shared/
plugins/
adapters/
runtime/
tests/
tools/
```

## Directory Roles

### `Docs/`
Human-readable design documents, migration notes, and architecture references.

### `controller/`
The orchestration service that discovers plugins, normalizes requests, routes calls, merges patches, and dispatches runtime commands.

### `schemas/`
JSON Schemas for request and response envelopes, manifests, commands, events, and owned state slices.

### `shared/`
Reusable SDK code, common models, error helpers, and client utilities.

### `plugins/`
One folder per plugin. Each plugin should contain a local app, Dockerfile, README, tests, and `plugin.yaml`.

### `adapters/`
System and hardware bridges such as motion, audio, battery, perception, peer transport, and CERBERUS integration.

### `runtime/`
Profiles, action maps, and policy files used at execution time.

### `tests/`
Contract, integration, simulation, and safety tests.

### `tools/`
Scripts for schema validation, manifest checking, registry generation, and simulation tooling.

## Per-Plugin Layout
```text
plugins/sweetie-plugin-example/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── config.py
│   └── services/
├── tests/
├── examples/
├── plugin.yaml
├── README.md
├── Dockerfile
└── requirements.txt
```

## Naming Conventions
- plugin directories: `sweetie-plugin-<domain>`
- adapter directories: `sweetie-adapter-<domain>`
- state slices: snake_case
- actions: `domain.verb`
- events: `domain.past_tense`

## Migration Advice
Some current plugins already resemble this shape. The main cleanup is to standardize contracts, deduplicate the SDK, and introduce authoritative schemas.
