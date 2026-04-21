# Requirements

**Project:** CERBERUS Companion Web Interface  
**Version:** 1.1  
**Date:** March 2026

---

## 1. System Requirements

### 1.1 Runtime (End User)

| Requirement | Minimum | Recommended |
|---|---|---|
| Browser | Chrome 110 / Firefox 115 / Safari 16 | Chrome 120+ |
| JavaScript | ES2020 (no build step required) | — |
| Screen resolution | 1024 × 768 | 1920 × 1080 |
| Network (live robot) | < 50 ms RTT to backend | < 20 ms LAN |
| Network (simulation) | None | — |
| OS | Any (browser-based) | Windows 10+, macOS 12+ |

### 1.2 Development

| Requirement | Details |
|---|---|
| Python | 3.9+ (for `python -m http.server` dev server) |
| Build tool | Bundler script (included) — strips ES module syntax, inlines modules |
| No npm, no Node.js, no webpack | Hard requirement — zero-install deployment must be preserved |

### 1.3 Backend (CERBERUS API)

| Requirement | Details |
|---|---|
| REST API | FastAPI, reachable at configurable base URL |
| WebSocket | `/ws` endpoint, auth via `?api_key=` query param |
| Telemetry | JSON messages at ≥ 10 Hz when connected to hardware |
| FunScript commands | `{ type: "funscript_command", action: "move", pos: 0-100, at_ms: number }` |
| Health endpoint | `GET /health` → `{ status: "ok" | "degraded" | "error" }` |

---

## 2. Functional Requirements

### 2.1 Control Layer

| ID | Requirement | Priority |
|---|---|---|
| CTL-01 | Operator can drive robot with keyboard (WASD + arrows) | Must |
| CTL-02 | Operator can drive robot with Xbox / standard gamepad | Must |
| CTL-03 | Operator can drive robot with dual virtual joystick on touchscreen | Must |
| CTL-04 | E-stop triggers within 100 ms of operator action | Must |
| CTL-05 | E-stop requires explicit confirmation (keyboard) or hold interlock (gamepad) | Must |
| CTL-06 | Commands are rate-limited to a configurable Hz (default 10 Hz) | Must |
| CTL-07 | All movement commands stop when connection is lost | Must |
| CTL-08 | Speed modes: normal, precision (0.3×), sprint (1.8×) | Must |
| CTL-09 | Keyboard bindings are user-configurable and persisted | Should |
| CTL-10 | Gamepad dead zones and sensitivity curves are configurable | Should |
| CTL-11 | Reduced-motion mode halves all speed multipliers | Should |
| CTL-12 | Input device indicator shows active source | Could |

### 2.2 Telemetry Layer

| ID | Requirement | Priority |
|---|---|---|
| TEL-01 | Battery level displayed with low-battery warning (< 20%) | Must |
| TEL-02 | Motor temperatures displayed with overtemp warning | Must |
| TEL-03 | Stale telemetry indicated when no update received for > 6 s | Must |
| TEL-04 | Fault codes displayed in human-readable form | Must |
| TEL-05 | WebSocket connection status always visible to operator | Must |
| TEL-06 | Simulation mode clearly labeled, distinct from live hardware | Must |
| TEL-07 | Telemetry timestamps shown | Should |
| TEL-08 | Derived health summary (OK / Degraded / Fault) | Should |

### 2.3 FunScript Engine

| ID | Requirement | Priority |
|---|---|---|
| FSC-01 | Import valid `.funscript` JSON files | Must |
| FSC-02 | Validate imported files: clamp pos, deduplicate timestamps, report warnings | Must |
| FSC-03 | Canvas editor: add points (right-click), delete (double-click), drag | Must |
| FSC-04 | Multi-select: shift-click and marquee drag | Must |
| FSC-05 | Undo/redo: ≥ 50 steps | Must |
| FSC-06 | Interpolation modes: Catmull-Rom, Linear, Step | Must |
| FSC-07 | Bézier interpolation mode | Should |
| FSC-08 | Playback: play, pause, stop, loop, speed control (0.1×–3.0×) | Must |
| FSC-09 | Scrub bar: drag to seek, arrow keys for fine control | Must |
| FSC-10 | Live hardware dispatch over WebSocket when connected | Must |
| FSC-11 | Export to `.funscript` file | Must |
| FSC-12 | Gaussian smoothing pass | Should |
| FSC-13 | Waveform generators: sine, ramp, triangle, square, random | Should |
| FSC-14 | Pattern snippet library: save/load named patterns in localStorage | Should |
| FSC-15 | A-B loop region markers | Should |
| FSC-16 | Snap-to-grid with configurable interval | Should |
| FSC-17 | Bookmark/chapter markers | Should |
| FSC-18 | Script statistics: duration, count, avg pos, peak velocity | Should |
| FSC-19 | Safety repair: detect and remove transitions below 15 ms interval | Must |
| FSC-20 | Copy/paste point selections | Should |
| FSC-21 | Drag-and-drop file import | Could |
| FSC-22 | Two-finger touch pan/zoom on timeline | Could |
| FSC-23 | Multi-axis framework skeleton (heave, sway, roll) | Could |

### 2.4 Diagnostics

| ID | Requirement | Priority |
|---|---|---|
| DIG-01 | API health check: GET /health with latency display | Must |
| DIG-02 | WebSocket connectivity test | Must |
| DIG-03 | Round-trip latency measurement | Must |
| DIG-04 | Browser capability report (Gamepad API, WebSocket, performance.now) | Should |
| DIG-05 | Connection log / audit trail visible to operator | Should |

### 2.5 Safety

| ID | Requirement | Priority |
|---|---|---|
| SAF-01 | E-stop accessible from all tabs | Must |
| SAF-02 | Watchdog timer disconnects commands after configurable inactivity | Must |
| SAF-03 | Simulation mode indicator present at all times when in sim | Must |
| SAF-04 | Low battery alert at configurable threshold (default 20%) | Must |
| SAF-05 | FunScript velocity safety check before hardware playback | Must |
| SAF-06 | Audit log of all E-stop events with timestamps | Should |
| SAF-07 | Operator safety briefing on first launch | Could |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Requirement | Target |
|---|---|
| UI frame rate in active telemetry | ≥ 30 fps |
| FunScript canvas render at 1000 points | < 16 ms per frame |
| E-stop dispatch latency (WS connected) | < 100 ms |
| Telemetry parse + render | < 5 ms |
| LocalHost.html file size | < 500 KB (uncompressed) |

### 3.2 Reliability

| Requirement | Target |
|---|---|
| WebSocket reconnect after drop | Automatic, exponential backoff 1–30 s |
| Zero crash on malformed backend telemetry | Required — all payloads validated |
| FunScript engine: no crash on corrupt file | Required — parser returns structured errors |
| All operations safe under rapid repeated input | Required — debouncing and guards on all command paths |

### 3.3 Accessibility

| Requirement | Standard |
|---|---|
| Keyboard-navigable interface | WCAG 2.1 AA |
| All interactive controls have visible focus ring | WCAG 2.1 AA |
| Color is not the sole indicator of status | WCAG 2.1 AA |
| Critical alerts use both color and icon/text | WCAG 2.1 AA |
| Reduced-motion mode respects OS preference | WCAG 2.1 AA |
| ARIA labels on all icon-only buttons | WCAG 2.1 AA |
| Minimum contrast ratio 4.5:1 on body text | WCAG 2.1 AA |

### 3.4 Security

| Requirement | Details |
|---|---|
| API key never stored in localStorage | Stored in sessionStorage only |
| No eval() or innerHTML with unsanitized data | All dynamic content HTML-escaped |
| No secrets bundled in source files | Verified by code review |
| Content Security Policy | Recommended for server deployments |
| Subresource integrity | Recommended for any CDN-sourced libraries |

### 3.5 Compatibility

| Requirement | Details |
|---|---|
| No build step for end users | Deployable as LocalHost.html without tooling |
| No runtime framework dependencies (React, Vue, etc.) | Plain JS only |
| No external CDN dependencies in LocalHost.html | All assets inlined |
| Works offline in simulation mode | Fully self-contained |

---

## 4. Compliance Requirements

| Standard / Regulation | Applicability | Implementation |
|---|---|---|
| Alberta OHS Code Part 36 (Robots), CAN/CSA-Z434 | Workplaces using robot in Alberta | E-stop, safe work procedure warnings, operator training documentation |
| WorkSafeBC OHS Regulation Part 12 | Workplaces in BC | Motion limits, safeguarding indicators |
| CCOHS Cobot Guidance | General Canadian workplace use | Psychosocial risk warnings, worker involvement guidance in docs |
| WCAG 2.1 AA | Accessibility | Keyboard nav, contrast, ARIA, reduced motion |
| ISO 9241-210 (HCD) | HCI design | User-configurable bindings, error prevention, learnability |

See [`docs/LegalDisclaimer.md`](LegalDisclaimer.md) for the full compliance and liability statement.

---

## 5. Out of Scope

The following are explicitly **not** requirements for the current release:

- Native mobile app (iOS/Android)
- Offline map building or SLAM in the browser
- Autonomous navigation command generation in the browser
- Multi-robot fleet management
- Video streaming transcoding in the browser
- User account management or authentication beyond API key
