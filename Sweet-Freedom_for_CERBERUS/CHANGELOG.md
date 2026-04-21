# Changelog

All notable changes to this project should be recorded here.

This changelog now serves two purposes:
- document what changed
- explain the project’s architectural direction for new contributors

---

## [Unreleased] — Platform transition era

This release line represents the move from a tool-centric controller toward a modular runtime-oriented robotics platform.

### Added
- clearer project-level documentation for past, present, and future direction
- architecture and roadmap design docs under `Docs/`
- stronger emphasis on modular runtime, safety, simulation parity, and plugin unification
- clearer statement of product goals for new users and contributors

### Changed
- README now explains the project as an evolving runtime/control platform, not just a controller UI
- project direction is now explicitly tied to source-of-truth research
- roadmap messaging shifted from feature accumulation to systems architecture
- UI and backend work are being framed around command flow, safety, and modular boundaries

### In progress
- modular UI decomposition
- command and runtime model cleanup
- safety-layer hardening
- event-driven state flow
- planning for canonical API and plugin-runtime unification

### Known architectural gaps
- in-process CERBERUS plugin model and out-of-process Sweetie plugin model are still not unified
- canonical versioned API contract is still incomplete
- command lifecycle is still emerging
- ROS2-facing adapter architecture remains largely design-stage
- diagnostics and replay infrastructure are still early

---

## [Legacy line] — Earlier controller-centric builds

Earlier iterations focused on:
- separate control surfaces
- hardcoded UI features
- narrower endpoint-driven control workflows
- early experiments around Sweetie-Bot features and FunScript-related expansion

These versions were useful for proving concepts and establishing a visible product surface, but they also exposed the need for a more durable architecture.

---

## Direction for upcoming milestones

### Near term
- command lifecycle and explicit runtime state
- ownership / keepalive semantics
- latching safety model
- command arbitration
- more coherent diagnostics and event flow

### Mid term
- canonical `/api/v1` contract
- plugin runtime unification
- mode-based UI
- richer simulation and adapter parity

### Longer term
- ROS2 profile support
- more capable plugin ecosystem
- stronger observability and replay
- safer autonomous / AI-assisted behaviors
