# CERBERUS Vision Document

**Version:** 1.1  
**Date:** March 2026  
**Status:** Active

---

## Mission Statement

CERBERUS is a commercial-grade, operator-trustworthy control and scripting interface for legged robotic platforms. Starting with the Unitree Go2, CERBERUS aims to be the definitive browser-based HMI for professional quadruped deployment — combining real-time telemetry, intuitive multi-modal control, and a powerful motion-scripting engine in a single zero-install application.

---

## Core Design Values

1. **Safety is non-negotiable.** Every feature ships with E-stop integration, operator warnings, and graceful degradation under network failure. The UI must never encourage unsafe robot operation.

2. **The operator trusts what they see.** Stale data is clearly labeled. Simulation is clearly distinct from live hardware. No data is shown without provenance.

3. **Power without complexity.** A new operator should be driving the robot within 60 seconds. An expert operator should be scripting complex sequences within 10 minutes.

4. **No install, no build step.** The entire application must remain deployable as a single HTML file. Zero npm, zero bundler requirement for the end user.

5. **Commercial-grade, not demo-grade.** All code is written as if a real operator will depend on it in a real-world deployment.

---

## Product Pillars

### Pillar 1 — FunScript Motion Engine
The primary commercial differentiator. CERBERUS is the only browser-based tool that allows importing, editing, and playing back FunScript-format motion sequences directly to a legged robot's body. The goal is parity with desktop FunScript editors (OFS-level feature completeness) while adding robot-specific safety constraints.

**Target capability:** Professional choreographers and researchers can produce a 60-second Go2 motion sequence, validate it in sim, apply safety repair, and push it to hardware in a single browser session.

### Pillar 2 — Unified Input System
An operator should be able to reach for any input device — phone touchscreen, Xbox controller, laptop keyboard — and drive the robot without reconfiguration. All devices converge on a single normalized control pipeline with configurable dead zones, sensitivity curves, and accessible reduced-motion modes.

### Pillar 3 — Real-Time Observability
The interface is the operator's primary window into the robot's state. Telemetry, fault indicators, video feeds, LiDAR overlays, behavior tree visualization, and audit logs must be available simultaneously and update in real time. Data older than 6 seconds is marked stale. No metric is shown without a timestamp.

### Pillar 4 — Compliance & Safety First
CERBERUS targets Alberta/Canadian regulatory environments. All software safety constraints (rate limits, velocity guards, E-stop, watchdog thresholds) are implemented by default. The interface provides the documentation and warnings needed for responsible deployment.

---

## Roadmap

### Phase 1 — Foundation (Complete: v1.0)
- Single-file deployable HTML interface
- REST + WebSocket backend integration
- Manual control: keyboard, gamepad, virtual joystick
- Basic FunScript import, playback, and canvas editor
- Simulation mode
- Battery, temperature, fault telemetry
- E-stop and safety watchdog
- Diagnostics suite

### Phase 2 — Editor & Input Maturity (Active: v1.1–v1.4)
- FunScript engine v2.0: undo/redo, waveform generators, pattern library, A-B loop, snap, bookmarks, statistics, validation, Bézier interpolation
- Unified input manager: configurable bindings, sensitivity curves, dead zones, accessibility
- Touch and tablet optimization for Manual tab
- Improved stale data handling with visual degradation
- Pattern snippet sharing (export/import pattern library)
- Multi-axis FunScript framework (heave, sway, roll) — schema defined, UI pending hardware support

### Phase 3 — Advanced Robotics Integration (v2.0)
- **LiDAR visualization:** Real-time 2D/3D point cloud display from Go2 LiDAR via CERBERUS API bridge (reference: YasiruDEX/Go2-Dynamic-Inspection ROS2 pipeline)
- **Spatial awareness panel:** Occupancy grid, obstacle distance indicators, no-go zones
- **Waypoint missions:** Click-to-navigate on a 2D map
- **Path recording:** Record operator-driven path and replay as mission
- **Behavior tree editor:** Visual BTree editing (currently view-only)
- **Plugin panel:** Full plugin management UI (install, configure, enable/disable)
- **WebRTC video stream:** Low-latency video feed from robot camera
- **Multi-robot support:** Session management for concurrent robot instances

### Phase 4 — Commercial & AI Features (v2.x)
- **Responsive layout v2:** Full drag-and-drop panel system (teleop console aesthetic)
- **FunScript auto-generation:** AI-assisted motion generation from natural language prompts
- **Anomaly detection:** Backend health metrics trigger predictive operator warnings
- **Audit export:** Full operator session logs exportable to CSV/JSON
- **API key management UI:** Rotate, revoke, scope keys without backend access
- **Offline-first:** Service worker caching for reliable field deployments
- **Electron wrapper:** Optional native app packaging for full-screen field laptop use
- **i18n completion:** Full French, Spanish translations (framework exists)
- **RBAC:** Role-based UI restrictions (viewer, operator, admin)

### Phase 5 — Platform (v3.x+)
- **Multi-platform support:** Abstract hardware bridge layer to support Go1, Spot, ANYmal, and other legged platforms
- **Script marketplace:** Sharing and rating community FunScript sequences
- **Certification pathway:** Documentation and test suite targeting CSA Z434 compliance artifacts
- **Cloud-assisted telemetry:** Optional backend telemetry relay for remote monitoring

---

## Competitive Landscape

| Product | Strengths | Gap CERBERUS fills |
|---|---|---|
| Unitree official app | Official, polished for consumers | No scripting, no extensibility, no operator telemetry |
| ROS2 + RViz | Full capability | Requires Linux, ROS, expert setup — no browser deployment |
| Boston Dynamics Scout | Professional UX reference | Commercial, locked to Spot hardware |
| OFS (OpenFunscripter) | Best-in-class script editor | Desktop only, no robotics output |
| Custom Python scripts | Flexible | No UI, no safety layer, no operator observability |

CERBERUS is uniquely positioned as the **only zero-install browser-based** platform combining professional HMI quality, FunScript motion scripting, and Unitree Go2 hardware integration.

---

## Success Metrics

| Metric | Target (Phase 2) |
|---|---|
| Time-to-drive for new operator | < 60 seconds |
| FunScript import → sim playback | < 30 seconds |
| E-stop latency (WS connected) | < 100 ms |
| Telemetry update rate (connected) | ≥ 10 Hz |
| Stale telemetry detection | ≤ 6 s threshold |
| Browser compatibility | Chrome 110+, Firefox 115+, Safari 16+ |
| Lighthouse accessibility score | ≥ 85 |
| Zero critical JS errors in sim mode | Pass |

---

## What CERBERUS Is Not

- Not a ROS node or ROS replacement
- Not a mobile app (though the UI supports mobile browsers)
- Not an autonomous AI decision-maker (AI features augment operator, never replace)
- Not a consumer toy — it controls a 12 kg motorized robot and treats that responsibility seriously
