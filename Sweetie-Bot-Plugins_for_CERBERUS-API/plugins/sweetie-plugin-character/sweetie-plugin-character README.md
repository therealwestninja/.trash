# Sweetie-Bot Reusable Plugin Pack

This bundle contains self-contained, container-ready plugins that can be used in three ways:

1. **Directly from the CERBERUS Web Controller** by calling each plugin's HTTP API.
2. **Alongside the CERBERUS Companion API** as sidecar services that extend robot control.
3. **From custom codebases** using simple HTTP requests or the included Python examples.

## Included plugins

- `sweetie-plugin-cerberus-bridge` — high-level robot command, macro, and safety wrapper service for the CERBERUS Companion API.
- `sweetie-plugin-character` — character reply, emote, and intent service for Sweetie-Bot style interactions.
- `sweetie-plugin-memory` — lightweight persistent session and key-value memory service.

## Quick start

```bash
cd plugins/sweetie-plugin-cerberus-bridge
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7010
```

Repeat for the other plugins on ports `7011` and `7012`.

## Docker Compose

A sample `docker-compose.yml` is included at the repo root.

```bash
docker compose up --build
```

## Integration targets

These plugins were designed against the endpoint patterns documented in the uploaded CERBERUS repos:

- CERBERUS Companion API REST endpoints such as `/state`, `/plugins`, `/motion/*`, `/behavior/goal`, `/safety/*`
- CERBERUS Web Controller expectations around plugin listings and direct HTTP access

They should be treated as a clean starting point for the new pluginized architecture, not as a claim of full live-hardware certification.
