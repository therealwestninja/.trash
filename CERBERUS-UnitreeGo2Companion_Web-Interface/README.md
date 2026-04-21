# CERBERUS Unitree Go2 Companion Web Interface

This repository is the web controller layer for the CERBERUS robotics stack and the emerging Sweetie-Bot plugin ecosystem.

**Backend** https://github.com/therealwestninja/CERBERUS-UnitreeGo2CompanionAPI  
**Interface (You are here →):** https://github.com/therealwestninja/CERBERUS-UnitreeGo2Companion_Web-Interface  
**Plugins:** https://github.com/therealwestninja/Sweetie-Bot-Plugins_for_CERBERUS-API

## Current direction

The controller is evolving from a fixed frontend into a flexible operator console that can:
- drive the CERBERUS backend
- monitor plugin health
- configure Sweetie plugin endpoints
- expose advanced robotics features without losing ease of use
- support both hobbyist use and advanced customization

## Main entrypoints

- `Control.html` — unified control interface with switchable LocalHost and PythonServer profiles
- `PythonServer.html` — compatibility redirect into `Control.html?profile=pythonserver`
- `LocalHost.html` — compatibility redirect into `Control.html?profile=localhost`

## Patch status

This patched build includes:
- Patch_1 modular input files
- Sweetie plugin stack settings/status card
- updated FunScript tab markup
- unified Control interface with switchable LocalHost / PythonServer operating profiles
- live-backend verification panel and PythonServer command locking until the controller looks like a real CERBERUS / Go2 session
- repository documentation refreshed under `/docs`

## Documentation

Start with:
- `docs/API_INTEGRATION.md`
- `docs/CHANGELOG.md`
- `docs/Controller_Team_Instructions.md`
- `docs/ROADMAP.md`

Repository documentation lives under `/docs`.

## Long-term goal alignment

The long-term goal is to support a realistic Sweetie-Bot AI that can safely roam, perceive, understand, and interact with the world. The controller should therefore be designed to expose:
- perception
- memory
- action selection
- plugin orchestration
- safety status
- advanced motion/gait control

## Quick use

- Open `Control.html` directly for the unified operator surface.
- Use the built-in profile switch to move between LocalHost / Demo and PythonServer / Go2 modes.
- `PythonServer.html` and `LocalHost.html` remain as compatibility redirects for older bookmarks and launch scripts.
- Use the Sweetie Plugin Stack card in Settings to point the UI at active plugin services.

## Sweetie v1 alignment

This build tracks the Sweetie-Bot integration-pack v1 controller expectations more closely by default:
- controller-side endpoint defaults now follow the 710x/720x integration-pack seed
- the Sweetie card exposes autonomy, social, dock/battery, peer, and adapter readiness summaries
- quick actions now cover safe stop, force dock, follow best friend, clear autonomy override, and peer status ping

## Validation

- JavaScript syntax can be spot-checked with `node --check sweetie.js`, `node --check control-profile.js`, `node --check cmd.js`, and other edited modules.
- A lightweight browser smoke harness now lives at `tests/sweetie-smoke.html`. Serve the repo locally, open that page, and confirm the PASS lines for readiness rendering and execute fallback behavior.
- In PythonServer mode, connect to a live backend and confirm the **Live Control Verification** card transitions from **LOCKED** to **LIVE VERIFIED** before movement/behavior controls become available.
