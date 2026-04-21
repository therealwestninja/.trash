# Architecture Overview

## Overview

Sweet Freedom is moving toward a layered architecture in which UI, runtime, safety, plugins, and hardware integration are clearly separated.

This is a practical response to the repo’s current integration gaps and to the source-of-truth recommendation that the system should converge on a single canonical API/WS schema, a unified plugin runtime abstraction, and a bridge/adaptor architecture that can support richer control without bypassing CERBERUS safety constraints. fileciteturn44file0L1-L1

---

## Core layers

### 1. UI layer
Responsibilities:
- operator controls
- state visualization
- diagnostics visibility
- safety surfaces
- mode- or capability-driven interaction

The UI should consume stable API and WebSocket contracts rather than direct implementation details.

### 2. API layer
Responsibilities:
- request validation
- versioned route contracts
- auth boundary
- compatibility aliases
- translation between UI and runtime semantics

### 3. Runtime layer
Responsibilities:
- canonical runtime state
- command and action lifecycle
- state transitions
- event emission
- cross-module orchestration

### 4. Safety layer
Responsibilities:
- E-Stop semantics
- armed/disarmed state
- comms-loss handling
- ownership/lease logic
- command approval, downgrade, or rejection

### 5. Plugin/runtime extension layer
Responsibilities:
- plugin discovery
- manifest loading
- capability or action execution
- unification of in-process and out-of-process plugin models

### 6. Adapter layer
Responsibilities:
- simulation adapter
- direct robot adapter
- ROS2-facing adapter
- transport-specific implementation behind stable higher-level contracts

---

## Desired flow

Operator / AI / automation  
→ action or command request  
→ arbitration  
→ safety gate  
→ runtime execution  
→ adapter  
→ telemetry and events  
→ runtime state / UI update

---

## Architectural principles

### Stable contracts over convenience
A little more structure at the boundaries reduces chaos later.

### High-level actions over low-level AI control
AI and plugins should not jump directly into unsafe low-level motion paths.

### Sim-first, adapter-clean development
Simulation and real-hardware paths should share the same high-level contracts whenever possible.

### Observability is part of the architecture
Diagnostics, event logs, and replayability are not optional extras.

### Compatibility during transition
Legacy routes and behaviors may need compatibility shims while the system converges on cleaner contracts.

---

## Immediate architectural priorities

- formalize action and result shapes
- strengthen runtime state assembly
- introduce session/ownership and keepalive semantics
- converge on a canonical API namespace
- add event-flow discipline and replay-friendly logs
- unify plugin models behind one runtime view
