# AI Continuation Playbook

This document is intended for AI systems like ChatGPT or Claude continuing development.

## Non-negotiable rules

- never collapse isolated plugins into a single monolith
- preserve `/execute`, `/health`, `/manifest`
- do not hardcode controller behavior into plugins
- do not hardcode plugin behavior into controller templates
- isolate hardware adapters from cognition/personality layers

## Next development priorities after this pack

1. Replace adapter stubs with real CERBERUS / GO2 bindings
2. Add person identity recognition for best-friend/supporting/public
3. Add stronger world model persistence
4. Add mission executive above autonomy supervisor
5. Add stuck/fall/comms-loss watchdog safety
6. Add real squad role coordination

## How to extend this pack safely

- add a new adapter under `adapters/`
- or add a new plugin under the main Sweetie ecosystem
- update `stack/docker-compose.yml`
- update `stack/configs/plugin-endpoints.json`
- add a scenario JSON under `stack/scenarios/`
- update `tests/integration_runner.py`

## Controller guidance

If the Controller App is missing something required:
- add config-based endpoint wiring
- add new debug/status widgets
- expose plugin health, autonomy mode, goal, focus target, docking state, peer state
- keep changes documented under `controller_patch/`
