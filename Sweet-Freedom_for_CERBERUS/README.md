# Sweet Freedom for CERBERUS

> A modular, safety-aware control platform for Unitree GO2 robots running CERBERUS, evolving toward a full runtime layer for controller, AI, plugins, and simulation.

---

## What this project is

Sweet Freedom began as an attempt to combine an existing CERBERUS controller interface with Sweetie-Bot AI ambitions into a single drop-in control stack for a Unitree GO2. The long-term goal is no longer “just a prettier UI” or “just another plugin bundle.” The goal is a coherent robotics control platform with a clean runtime, safe command flow, simulation parity, and room for AI-driven behaviors.

In plain terms, this project is moving from:

- a pile of tools and panels

to:

- a modular robotics operating layer with a controller UI on top

That shift is grounded in the repository’s own source-of-truth research, which identifies the biggest remaining gaps as architectural integration, stable API contracts, unified plugin runtime, and a ROS2-capable adapter boundary rather than a lack of code everywhere. The current backend already has meaningful pieces in place, including a FastAPI app, safety and motion endpoints, in-process plugin loading, and a WebSocket event-forwarding path, while the Sweetie plugin side already defines an out-of-process HTTP plugin contract with schemas and a multi-service compose stack. fileciteturn44file0L1-L1 fileciteturn45file0L1-L1

---

## Where we came from

### Legacy controller phase

The project started in a more tool-oriented form:

- split interfaces such as LocalHost and PythonServer
- hardcoded feature paths
- control surfaces growing panel by panel
- minimal abstraction between UI, runtime behavior, and hardware logic

That approach helped get visible features on screen quickly, but it also created coupling. Features were hard to reuse, hard to test, and hard to extend. The UI grew around tools instead of modes, and the backend could feel more like a collection of endpoints than a stable runtime.

### Why that had to change

The research and repo review showed that the repo already had real pieces, but they were not yet organized like a durable product platform. The main blockers were identified as:

- reconciling CERBERUS in-process plugins with Sweetie’s out-of-process HTTP plugin model
- stabilizing a canonical REST and WebSocket contract
- introducing a bridge/adaptor layer that can support more serious ROS2-style capabilities without bypassing safety
- moving from hardcoded UI panels to manifest- or capability-driven presentation

Those are platform problems, not “add another button” problems. fileciteturn44file0L1-L1

---

## Where we are now

We are in the middle of a structural transition.

### Current direction

The project is being reorganized around a few core ideas:

- explicit runtime state
- modular UI components
- safer command flow
- a future command lifecycle
- unified simulation and real-hardware boundaries
- event-driven updates
- capability- and plugin-oriented expansion

The UI side has already been moving in that direction, with increasingly modular front-end pieces and a shift toward a cleaner runtime-driven interface. The broader architecture direction is now aligned with patterns seen in mature robotics ecosystems: actions with goal/feedback/result, ownership and keepalive, latching safety stops, command arbitration, sim/real parity, and better observability. fileciteturn46file0L1-L1

### What is already true today

Even before the full architecture lands, several important truths are already established:

- Sweet Freedom is not being treated as a toy UI anymore
- safety is a first-class concern
- simulation is not an afterthought
- plugin/runtime unification is a core design target
- documentation now reflects a product trajectory instead of a loose concept

---

## Where we are going

Sweet Freedom is becoming a platform with a stable spine.

### The target shape

The target architecture is centered on:

1. a canonical backend API and WebSocket contract  
2. a unified plugin runtime abstraction  
3. a command lifecycle with safety gating  
4. a simulation adapter and a real robot adapter  
5. a mode-based controller UI  
6. observability, diagnostics, and replay-friendly event flows  

The source-of-truth research recommends treating the most important next architectural gains as transferable control-system patterns from mature ecosystems, especially:

- goal/feedback/result actions
- explicit ownership and keepalive
- latching E-Stop semantics
- command arbitration across multiple intent sources
- simulation/real interface parity
- diagnostics, logging, record/replay, and integration testing

Those are the pieces that make any robotics controller feel real, safe, and testable. fileciteturn46file0L1-L1

---

## Roadmap

### Phase 1 — Runtime foundation
Focus: make the controller trustworthy as a system.

Planned direction:
- canonical action model
- explicit runtime state
- event bus / event forwarding discipline
- safety state machine
- session ownership and keepalive
- command arbitration between input sources

### Phase 2 — Canonical API and plugin unification
Focus: make the backend consistent and extensible.

Planned direction:
- `/api/v1` versioned contract
- compatibility aliases for legacy routes
- unified in-process and HTTP plugin runtime
- manifest-driven plugin execution pathways
- structured error envelopes
- stronger WebSocket contracts

### Phase 3 — UI overhaul
Focus: move from tool-based UI to mode-based UI.

Planned direction:
- mode-oriented layout
- command/goal panel
- diagnostics and safety views
- plugin cards driven by runtime/capabilities
- telemetry panels with better observability

### Phase 4 — Adapter and ecosystem expansion
Focus: make the platform bridge outward cleanly.

Planned direction:
- simulation parity improvements
- ROS2 adapter layer
- richer telemetry and sensor bridging
- optional navigation and autonomy integrations
- better plugin packaging and deployment profiles

---

## What new users should know

If you are new here, the important thing to understand is this:

Sweet Freedom is in active architectural transition.

That means:
- some parts are already modular and improving quickly
- some parts are still placeholder or transitional
- docs are now meant to explain the path, not pretend every future system already exists

You should evaluate the project as:
- a real control platform under construction
- not a finished commercial robotics stack
- not just a theme pack over existing code

---

## Recommended reading

Start here:

- `CHANGELOG.md`
- `Docs/Project_History_and_Roadmap.md`
- `Docs/Architecture_Overview.md`
- `Docs/Command_and_Safety_Model.md`
- `Docs/Plugin_Runtime_Unification.md`
- `Docs/Platform_Benchmark_Notes.md`

Source-of-truth research reports live under:

- `Docs/Source-of-Truth_Do-Not-Modify/`

Those reports are the basis for the direction described here and should be treated as preserved reference material. fileciteturn44file0L1-L1 fileciteturn46file0L1-L1

---

## Vision

Sweet Freedom aims to become an open, modular, safety-conscious control layer for advanced robot interaction on CERBERUS-powered GO2 systems.

That includes:
- manual control
- AI-assisted control
- simulation-first development
- plugin-driven expansion
- a runtime that can grow without collapsing under its own features
