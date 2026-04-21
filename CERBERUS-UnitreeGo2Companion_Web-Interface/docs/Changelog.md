## 2026-03-30 — Unified control follow-through: live verification lock
- Added PythonServer live-backend verification in `control-profile.js` using `/health`, `/ready`, `/state`, `/capabilities`, and `/plugins` probes.
- Added visible Live Control Verification status card to `Control.html`.
- Locked PythonServer operator controls until live verification succeeds; E-stop and connection/profile controls remain available.
- Added a fail-closed guard in `cmd.js` so blocked live commands are rejected even if UI disabling is bypassed.

# Changelog

## [1.0.3] — 2026-03-30 — Unified Control interface

### Added
- added `Control.html` as the single unified operator interface for both LocalHost / Demo and PythonServer / Go2 use cases
- added `control-profile.js` to manage interface profile selection, persistence, profile-aware connection messaging, and safe mode transitions

### Changed
- converted `PythonServer.html` and `LocalHost.html` into compatibility redirects that open the unified control surface with the correct profile preselected
- updated startup flow so the LocalHost profile prefers browser simulation while the PythonServer profile prompts for authenticated backend connection
- refreshed operator copy and settings UI so profile intent is visible in the header, home banner, settings, and auth modal

### Fixed
- removed the largest remaining source of HTML drift between the two legacy entrypoints by consolidating them behind one shared interface

## [1.0.2] — 2026-03-30 — Sweetie lifecycle + smoke coverage

### Added
- added a dedicated Sweetie command lifecycle panel to both controller entrypoints so operators can see queued/running/completed command state, attempts, timing, and fallback details
- added `tests/sweetie-smoke.html` and `tests/sweetie-smoke.js` for a lightweight browser-served Sweetie integration smoke test covering readiness rendering and execute fallback behavior

### Changed
- enriched Sweetie command history entries with attempt counts, start/finish timestamps, and durations
- exposed lightweight Sweetie test hooks for smoke-page validation without coupling production UI to a heavy test framework

### Fixed
- removed a runtime-breaking stray quick-action confirmation block from `initSweetieIntegration()`
- corrected another stale docs reference in `docs/API_INTEGRATION.md`

## [1.0.1] — 2026-03-30 — Sweetie integration alignment

### Changed
- updated Sweetie default endpoint wiring to match the integration-pack v1 seed (710x core services and 720x adapters)
- expanded controller quick actions to include safe stop, force dock, clear autonomy override, and peer status ping
- added operator-facing Sweetie status cells for autonomy, best-friend focus, dock/battery, peer state, and adapter readiness

### Fixed
- removed duplicate LocalHost refresh listener that triggered redundant Sweetie status probes
- corrected README documentation paths that pointed at a non-existent `/Docs` tree

All notable changes to the CERBERUS Companion Web Interface are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **`funscript.js` v2.0** — Complete rewrite of the FunScript engine:
  - 100-step undo/redo history (Ctrl+Z / Ctrl+Y)
  - Copy/paste of selected point ranges (Ctrl+C / Ctrl+V)
  - Waveform generator: sine, ramp, triangle, square, random
  - Pattern library: save/load named point patterns to localStorage
  - A-B loop region markers with canvas shading
  - Snap-to-grid with configurable grid interval (ms)
  - Bookmark/chapter markers with labels and colors
  - Script statistics panel: duration, action count, avg pos, peak velocity, safety warning
  - Validation and auto-repair: detects and removes unsafe high-velocity transitions (< 15 ms interval with > 10 pos-unit Δ)
  - Multi-axis framework skeleton (heave/y, sway/x, roll) — ready for future multi-axis hardware
  - Bézier interpolation mode added alongside existing Catmull-Rom, Linear, Step
  - Full touch support: two-finger pinch-zoom and pan on the timeline canvas
  - Drag-and-drop `.funscript` file import directly onto canvas
  - Keyboard shortcuts: Space=play/pause, F=fit, I=invert, Home/End=scrub bounds, arrow keys=scrub/nudge
  - Import parser: validates all fields, clamps out-of-range pos, deduplicates timestamps, reports warnings to console

- **`input.js` v2.0** — New unified input abstraction layer replacing separate keyboard/gamepad event handlers:
  - User-configurable key bindings persisted in localStorage (Remap / Clear / Reset)
  - Sensitivity curves: linear, square, cube
  - Per-axis dead zone (configurable, default 0.12)
  - Multi-device priority: joystick > gamepad > keyboard
  - Reduced-motion mode: respects `prefers-reduced-motion` media query, halves all speed multipliers
  - ARIA live region for screen-reader announcements
  - Device indicator widget shows active input source
  - Gamepad E-stop interlock: LB + RB + B held 1.5 s (configurable buttons and hold time)
  - LT/RT analog triggers for precision/sprint speed scaling
  - Input suppressed automatically when form fields have focus

### Changed
- `README.md` — Comprehensive rewrite with full controls reference, FunScript feature table, architecture diagram, compliance section, and related projects table
- `docs/LegalDisclaimer.md` — Full legal and safety document (created)
- `docs/Requirements.md` — Technical and product requirements (created)
- `docs/Vision_Document.md` — Long-term product direction (created)

### Fixed
- FunScript: marquee selection now correctly selects all points within box bounds
- FunScript: drag multi-point move no longer leaves ghost points after undo
- Input: keyboard commands no longer fire when Settings or FunScript text inputs have focus
- Input: gamepad axes no longer drift due to missing dead zone on LT/RT triggers

---

## [1.0.0] — 2026-03-29 — Initial Deployment Release

### Added
- `LocalHost.html` — self-contained single-file deployment with all modules inlined
- `PythonServer.html` — development entry point using modular source files
- `start_server.bat` — one-click Windows development server
- `auth.js` — sessionStorage API key management, connect/disconnect flow
- `ws.js` — WebSocket client with exponential backoff reconnect (1 s → 30 s cap)
- `cmd.js` — command rate limiter and dispatch queue
- `telemetry.js` — telemetry parser with stale-data detection (6 s threshold)
- `fsm.js` — frontend finite state machine for robot behavioral states
- `canvas.js` — LiDAR / sensor visualization canvas
- `plugin-status.js` — backend plugin status panel
- `joystick.js` — dual virtual joystick (multi-touch validated layout)
- `keyboard.js` — keyboard movement handler (10 Hz rate limited)
- `gamepad.js` — Xbox gamepad handler (Gamepad API)
- `funscript.js` v1.0 — FunScript timeline editor with Catmull-Rom/Linear/Step interpolation, Gaussian smoothing, hardware playback
- `diagnostics.js` — connectivity, latency, browser diagnostics suite
- `behaviors.js` — behavior library with category filter
- `metrics.js` — health Hz, Prometheus, plugin status display
- `ui.js` — tab system, panel management, toast notifications
- `animation.js` — procedural animation clips
- `simulation.js` — browser-local 20 Hz simulation loop
- `config.js` — configuration root module
- `i18n.js` — internationalization framework
- `ai.js` — Anthropic AI integration (local key, never sent to backend)
- `main.js` — module orchestrator, window._* hook registration
- `companion.css` — robotics console dark theme
- `docs/API_INTEGRATION.md` — backend REST/WS contract documentation
- `docs/ARCHITECTURE.md` — system architecture diagrams
- `LICENSE` — MIT

### Security
- API key stored in `sessionStorage` only (cleared on tab close)
- All backend-sourced content HTML-escaped before DOM insertion
- No credentials or secrets bundled in source files
- WebSocket connection uses `?api_key=` query parameter (browser WS API limitation)

---

## Version Strategy

| Range | Meaning |
|---|---|
| 1.x.x | Stable: compatible with CERBERUS API v1 |
| 2.x.x | Next: breaking API schema changes, major UI redesign |
| 0.x.x | Pre-release: no stability guarantees |

Patch releases (x.x.N) fix bugs without changing API contracts.  
Minor releases (x.N.x) add features in a backward-compatible manner.  
Major releases (N.x.x) may break existing `.funscript` files or API contracts — migration notes will be provided.


## 2026-03-30 — Sweetie controller patch v2
- added LocalHost parity patch for Sweetie UI additions
- added `localhost_patch.js`
- aligned developer documentation references to the existing lowercase `docs/` tree
- expanded README to reflect plugin-oriented controller direction
