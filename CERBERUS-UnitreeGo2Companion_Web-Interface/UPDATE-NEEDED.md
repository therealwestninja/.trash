# UPDATE-NEEDED

## Objective
Inspect the current Sweetie-Bot integration pack against this controller repo, update the controller where the mismatch was low-risk to correct immediately, and catalogue the remaining work needed to stay aligned.

## Immediate issues found and fixed

### 1. Outdated Sweetie endpoint defaults
- **Problem:** `sweetie.js` still defaulted to the older 7000–7008 layout and legacy service names (`runtime`, `worldModel`, `memory`).
- **Why it matters:** the updated Sweetie integration pack seeds controller config with the 7101–7106 core services and 7201–7205 adapters. A fresh controller install would probe the wrong ports and mislabel several services.
- **Fix applied:** migrated defaults to the current seed, added `perceptionAdapter`, and added legacy-key migration so older saved configs continue to load.

### 2. Operator quick-action coverage lagged behind controller patch guidance
- **Problem:** the UI only exposed follow and patrol shortcuts.
- **Why it matters:** the current Sweetie controller patch explicitly calls for minimum operator controls like safe stop, force dock, clear autonomy override, and peer status ping.
- **Fix applied:** added the missing quick actions in `sweetie.js` and wired new buttons into both HTML entrypoints.

### 3. Missing high-value Sweetie state summaries in the card
- **Problem:** the card could probe plugins, but it did not surface the status categories the updated Sweetie docs now call out: autonomy mode/goal, best-friend state, dock/charge state, peer state, and adapter health.
- **Fix applied:** added controller/plugin-family summary cells and compatibility notes populated from probe results.

### 4. LocalHost parity bug: duplicate refresh listener
- **Problem:** `localhost_patch.js` bound an extra refresh click handler after `initSweetieIntegration()` already registered one.
- **Impact:** one click could trigger duplicate Sweetie probes and duplicate log noise.
- **Fix applied:** removed the redundant listener.

### 5. Broken README documentation pointers
- **Problem:** `README.md` referenced a non-existent `/Docs` tree and files that are not present in this repository.
- **Impact:** onboarding/document navigation was broken out of the box.
- **Fix applied:** repointed README links to the actual lowercase `/docs` files in the repo.

## Additional issues found that still need follow-through

### A. Controller-side contract standardization is still partial
- The UI probes `/execute`, `/capabilities`, `/session`, `/behavior`, `/plugins`, and `/terrain`, but the backend repo still looks mixed in how much of the higher-level Sweetie controller contract is formally exposed.
- The frontend now degrades more cleanly, but the backend should formalize:
  - a stable controller `/execute` envelope
  - a stable `/capabilities` response
  - explicit autonomy/override/dock/focus fields in `/state` or `/behavior`

### B. Command lifecycle surface is now partially addressed
- Added a dedicated Sweetie command lifecycle panel in both HTML entrypoints and enriched command history with attempts, timestamps, and durations.
- Remaining gap: this is still a local UI surface, not a controller-backed acknowledgement stream. Backend acknowledgement IDs / queue states should still be formalized.

### C. Lightweight frontend validation harness now exists
- Added `tests/sweetie-smoke.html` and `tests/sweetie-smoke.js` for browser-served smoke validation of readiness rendering and standard→legacy execute fallback behavior.
- Remaining gap: this is still a lightweight smoke harness, not a CI-backed headless regression suite.

### D. Unified control surface is now in place
- Added `Control.html` as the single shared operator interface.
- `PythonServer.html` and `LocalHost.html` now act as lightweight compatibility redirects that preselect the correct operating profile.
- Added `control-profile.js` so operators can switch between LocalHost / Demo and PythonServer / Go2 modes from inside the UI without maintaining two divergent HTML entrypoints.

### E. Runtime regression surfaced during follow-through and is now fixed
- While implementing the lifecycle work, a stray `spec.confirm` block inside `initSweetieIntegration()` was found. It referenced undefined locals and could break Sweetie initialization at runtime.
- Fix applied in this pass.


### F. PythonServer live-backend verification and command gating are now in place
- Added profile-aware live verification in `control-profile.js` that probes `/health`, `/ready`, `/state`, `/capabilities`, and `/plugins` before unlocking live-command surfaces.
- Added a visible verification panel to the unified `Control.html` settings view so operators can see why commands are locked or unlocked.
- Added a frontend control lock for PythonServer mode so movement / behavior / script controls stay disabled until the backend presents enough evidence of a real CERBERUS / Go2 session.
- Added a second guard in `cmd.js` so blocked live commands fail closed even if a UI element somehow bypasses the disabled state.

### G. Remaining follow-through
- Verification is intentionally heuristic because the backend still does not expose a formal "hardware live / simulation / bridge attached" contract. The best long-term backend fix is a dedicated, versioned readiness field such as `hardware.mode`, `bridge.connected`, and `robot.platform`.
- The frontend now locks most operator command surfaces in PythonServer mode until verification passes, but this should later be backed by server-side command policy enforcement as well.

## Files changed in this pass
- `Control.html`
- `control-profile.js`
- `main.js`
- `cmd.js`
- `ws.js`
- `companion-additions.css`
- `PythonServer.html`
- `LocalHost.html`
- `sweetie.js`
- `localhost_patch.js`
- `README.md`
- `docs/CHANGELOG.md`
- `docs/API_INTEGRATION.md`
- `tests/sweetie-smoke.html`
- `tests/sweetie-smoke.js`

## Validation run performed
- JavaScript syntax check with Node on the edited JS modules
- Manual static inspection of the unified `Control.html` surface and both compatibility redirects

## Notes
- This pass intentionally avoided inventing backend-only contracts that are not present yet. The new quick actions therefore keep the existing direct-plugin `/execute` fallback behavior.
- Saved configs from the prior Sweetie endpoint key layout should still load because the new config loader migrates legacy keys into the updated layout.
