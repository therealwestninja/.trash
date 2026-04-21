# CERBERUS Companion — Roadmap

## Current State: v3.0 (Local-File Operational)

All core systems functional in `LocalHost.html` (no server required).

---

## Phase 1 — MVP Stabilisation (Now → v3.5)

**Goal:** Reliable, usable, safe demo on real hardware.

- [x] Modular JS architecture (19 focused modules)
- [x] WebSocket reconnect with exponential backoff
- [x] Dual joystick (touch + mouse)
- [x] Xbox/Standard Gamepad support with deadzone + haptics
- [x] Keyboard hold-to-move with shortcut overlay
- [x] FunScript engine — parse, Catmull-Rom interpolation, canvas editor, hardware output
- [x] Diagnostics suite — HTTP, WS, latency, browser capabilities
- [x] Plugin status display (stair, payload, limb loss)
- [x] Stale telemetry detection
- [x] Legal disclaimer (Alberta OHS, WorkSafeBC, CCPSA context)
- [ ] Video feed placeholder (WebRTC signaling path)
- [ ] Keyboard remapping UI (bindings editor)
- [ ] `LocalHost.html` auto-bundler on source change

## Phase 2 — Beta (v3.5 → v4.0)

**Goal:** Suitable for field testing with real Go2 hardware.

- [ ] Video feed: WebRTC + MJPEG fallback
- [ ] LiDAR 2D occupancy overlay (canvas-based)
- [ ] FunScript audio sync (Web Audio API offset tracking)
- [ ] Input binding editor with per-axis sensitivity curves
- [ ] Session recording (command log replay)
- [ ] Multi-robot selector (backend provides robot list)
- [ ] PWA manifest (installable on tablet)
- [ ] CERBERUS API v2 compatibility layer

## Phase 3 — Commercial Release (v4.0+)

**Goal:** Commercial viability — product quality, documentation, compliance.

- [ ] Role-based access (operator vs. read-only observer)
- [ ] Encrypted credential storage (Web Crypto API)
- [ ] Audit trail export (CSV/JSON safety log)
- [ ] Accessibility pass (WCAG 2.1 AA)
- [ ] Offline operation with service worker caching
- [ ] Plugin UI SDK (third-party panel extensions)
- [ ] Map / waypoint planner
- [ ] Multi-robot orchestration
- [ ] Formal safety case document (IEC 62061 reference)

---

## Deferred (Under Evaluation)

- ROS2 bridge visualization (requires backend support)
- AR overlay (WebXR)
- On-device AI inference (WASM/ONNX)
