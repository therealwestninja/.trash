# Sweetie-Bot Architecture Overview

## Purpose
This package defines a consistent plugin architecture for Sweetie-Bot so the project can evolve from a prototype plugin collection into a stable character runtime with clean controller orchestration, explicit state ownership, and safe action dispatch.

It is designed around the project priorities in the team brief:
- Mission Executive as a high-priority system
- Mood-driven behavior and expression
- Social awareness and best-friend prioritization
- Modular plugins with one system per plugin
- Safe real-world autonomy

## Core Principles
1. **One system per plugin**
   Each plugin should own one domain. It can read shared state but should not become a grab-bag of unrelated logic.

2. **No tight coupling**
   Plugins should not import each other directly for business logic. They communicate through standard API calls, events, and command contracts.

3. **Controller as orchestrator, not brain**
   The controller routes calls, merges patches, fans out events, enforces safety, and records traces. It should not contain mission, mood, or social logic.

4. **Cognition separated from runtime execution**
   Thinking plugins should output state patches, events, and action intents. Hardware-facing code belongs behind the safety layer and runtime adapter.

5. **Authoritative state ownership**
   Every top-level state slice has one owner plugin. That prevents conflicting writes and makes debugging much easier.

## Four-Layer Model

### 1. Controller Layer
Responsible for:
- Plugin discovery
- Manifest loading
- Request normalization
- Orchestration flow
- State merge
- Event fanout
- Trace logging
- Safety gate before dispatch

### 2. Cognition Layer
Typical plugins:
- Mission Executive
- Mood
- Social
- Attention Manager
- Behavior Engine
- World Model
- Memory

These plugins reason about goals, context, emotion, social priority, and behavior selection.

### 3. Character Output and Action Layer
Typical plugins:
- Expressive Behavior
- Dialogue Style
- Voice Intent
- Action Registry
- Safety Layer
- Runtime Adapter

These plugins convert selected behavior into safe, executable, high-level actions.

### 4. Adapter Layer
Typical services:
- Motion adapter
- Audio adapter
- Battery adapter
- Perception adapter
- Peer transport adapter
- CERBERUS bridge

Adapters translate standardized commands into platform-specific behavior.

## Standard Plugin Surface
Every production plugin should support:
- `POST /execute`
- `GET /health`
- `GET /manifest`
- `GET /status` recommended
- `POST /reset` optional for testing and simulation
- `POST /configure` optional for runtime tuning

## Standard Execute Model
Every plugin receives a common request envelope and returns a common response envelope.
This lets the controller handle plugins consistently and allows tooling, tests, traces, and dashboards to scale.

The request includes:
- metadata
- session info
- context
- current shared state
- normalized input
- policy hints

The response includes:
- `result`
- `state_patch`
- `events`
- `commands`
- `warnings`
- `errors`

## Why this design matters
This structure keeps Sweetie-Bot extensible without losing character consistency. It gives you a clean path from:
- local simulation
- to multi-plugin orchestration
- to safe physical deployment

without rewriting the core contracts every time the system grows.
