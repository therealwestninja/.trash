# Shared Sweetie Plugin SDK

This SDK is the recommended shared contract layer for new or migrated plugins.

## Why it exists
The current repo contains several duplicated `sweetie_plugin_sdk` folders inside plugins. This shared package is intended to replace that drift over time.

## Contains
- Pydantic request and response models
- structured events, commands, and errors
- manifest loader
- simple HTTP client helper

## Migration approach
New plugins should import from `shared/sweetie_plugin_sdk`.
Existing plugins can migrate gradually.
