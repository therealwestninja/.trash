# Project History and Roadmap

## Purpose of this document

This file explains the development road in a more human-readable way than a changelog. It is intended for new contributors, reviewers, and anyone trying to understand why the project looks the way it does today.

---

## 1. Origin

Sweet Freedom grew out of a desire to combine:

- the CERBERUS controller experience
- the Sweetie-Bot AI/plugin ambitions
- a Unitree GO2 control surface that felt more unified

At first, the easiest path was feature-first development:
- add control pages
- add endpoints
- add experiments
- keep moving

That got visible progress fast, but it also produced a system that was better at demonstrating potential than sustaining complexity.

---

## 2. The early shape

The early shape of the project was strongly tool-oriented.

Common symptoms:
- separate interfaces for different operating contexts
- features added in place rather than behind stable abstractions
- UI growth driven by visible controls
- limited command lifecycle structure
- runtime behavior mixed with presentation concerns

This stage was useful because it exposed what users wanted and what the repo needed. It also made clear that polishing visuals alone would not make the platform feel real.

---

## 3. What changed our direction

The source-of-truth research clarified that the biggest missing pieces were architectural, not cosmetic.

The reports identified three especially important realities:

1. the project already contains substantial backend infrastructure  
2. the hardest unresolved work is integration work  
3. the best next steps are to adopt proven robotics-platform patterns rather than inventing everything from scratch  

Examples include:
- stable API contracts
- unified plugin runtime
- safety-aware command flow
- ROS2-capable bridge architecture
- better ownership, keepalive, and observability patterns fileciteturn44file0L1-L1 fileciteturn46file0L1-L1

---

## 4. Present transition

The current era is best described as a transition from “controller project” to “runtime platform.”

That means the project is now optimizing for:
- modularity
- safety
- explicit state
- interoperability
- testability
- future plugin and adapter growth

This is why recent work has focused so heavily on:
- UI modularization
- runtime state cleanup
- safety gating
- WebSocket/event flow
- documentation

---

## 5. Near-term roadmap

### Priority A — make the control loop trustworthy
This is the vertical slice:
operator input → intent/action → safety gate → execution path → response → visible state

### Priority B — make the contracts explicit
This includes:
- canonical API paths
- stable action and state shapes
- clearer route/request/response boundaries
- command/event semantics

### Priority C — unify extension models
Sweet Freedom cannot scale cleanly while:
- one part of the system assumes in-process plugins
- another part assumes out-of-process HTTP plugins

A unified runtime view is necessary.

### Priority D — harden for real operation
This includes:
- ownership / session concepts
- keepalive and comms-loss behavior
- latching E-Stop semantics
- diagnostics and replay
- safer adapter boundaries

---

## 6. Longer-term roadmap

Longer-term success looks like this:

- a stable runtime core
- a capability- or manifest-driven extension system
- simulation and real robot parity at the adapter boundary
- a mode-based UI
- a ROS2-friendly bridge path
- AI assistance layered on top of safe high-level actions rather than unsafe low-level control

---

## 7. What not to mistake for progress

The project has learned that some things feel like progress but do not actually stabilize the platform.

Examples:
- adding more UI surface without improving runtime contracts
- piling on features without arbitration or safety semantics
- pretending plugin growth equals architecture
- chasing aesthetics before system clarity

That does not mean UI polish is unimportant. It means polish should ride on top of a better spine.

---

## 8. Success criteria

This project is succeeding when:
- new users can understand what it is trying to become
- developers can add features without creating chaos
- safety rules are explicit
- simulation work transfers cleanly to real adapters
- command flow becomes observable and testable
- docs stay honest about what exists now versus what is planned
