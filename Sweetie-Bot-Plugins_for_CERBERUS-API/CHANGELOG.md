# Changelog


## 1.0
 The first **real hardware loop** package for the Sweetie-Bot ecosystem.

It is designed to connect:
- the CERBERUS Controller App
- the Sweetie-Bot plugin ecosystem
- real or near-real hardware adapters for a Unitree GO2 / CERBERUS backend

- a full integration architecture
- a docker-compose stack for the core ecosystem
- adapter stubs for:
  - perception input
  - audio I/O
  - motion output
  - battery/charging state
  - peer transport
- scenario runner for end-to-end demo flows
- contract/integration test harness
- controller integration configuration
- design docs for AI-assisted continuation

**Best friend follow + low-battery dock loop**

1. Perception sees best friend
2. Social bonding resolves priority
3. Attention selects focus
4. Cognition/autonomy choose follow mode
5. Behavior shapes response
6. TTS emits speech envelope
7. Action registry resolves follow action
8. Runtime sends motion through motion adapter
9. Battery drops below threshold
10. Autonomy transitions to dock mode
11. Docking adapter returns approach/alignment cycle
12. Charging state is entered

- `stack/` — compose stack, endpoints, env, scenario seeds
- `adapters/` — hardware adapter services
- `tests/` — contract + integration harness
- `controller_patch/` — controller-side integration configuration and docs
- `docs/` — architecture and continuation docs
- `tools/` — scenario runner and health utilities


## 0.0.8

- expanded persona assets to include default emotes, accessory scenes, and routine tags
- moved more of the emote, routine, and accessory groundwork into reusable CERBERUS-style plugins
- added `GET /character/foundation` for authoring-oriented runtime metadata
- added `GET /emotes`
- added `GET /routines/{routine_id}/plan`
- added `GET /accessories/scenes` and `POST /accessories/scene`
- accessory state is now asset-driven rather than a flat boolean-only response
- character state now tracks active emote and active accessory scene
- refreshed README and documentation for the plugin-focused foundation pass

## 0.0.7

- added OpenAI and Anthropic dialogue provider scaffolds
- added configurable CERBERUS onboard audio adapter
- added `/character/llm`
- updated console scaffold with LLM and audio status
