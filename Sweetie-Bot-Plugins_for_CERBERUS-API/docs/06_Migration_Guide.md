# Migration Guide for the Existing Repo

## What this package adds
This package introduces a cleaner architecture layer without forcing an immediate rewrite of every plugin.

Included additions:
- human-readable architecture docs in `Docs/`
- machine-readable JSON Schemas in `schemas/`
- a shared Python SDK in `shared/sweetie_plugin_sdk/`
- a controller skeleton in `controller/`
- a reference plugin template in `templates/reference-plugin/`

## Recommended Migration Strategy

### Step 1
Adopt the shared SDK for new plugins first.
Do not block existing plugins.

### Step 2
Update the controller to accept the new request and response envelope.
Add compatibility shims for old plugins if needed.

### Step 3
Start with the high-value plugins:
- mission executive
- mood
- social
- behavior engine

### Step 4
Move duplicate `sweetie_plugin_sdk` copies out of plugin folders over time.
Point plugins at the shared SDK.

### Step 5
Enable manifest and schema validation in CI.

## Practical Notes
- Existing plugins can continue to expose `/execute`, `/health`, and `/manifest`.
- If an old plugin uses `type` and `payload` instead of the new envelope, the controller can translate temporarily.
- State ownership checks should begin in warning-only mode, then switch to enforcement after the main plugins are updated.

## Immediate Wins
Even before every plugin is migrated, you can get value from:
- consistent docs
- standardized manifests
- shared schemas for new code
- a reference controller flow
