/**
 * ws.js — WebSocket lifecycle, reconnect strategy, and inbound message routing.
 *
 * Single responsibility: own the WS connection from open to close and back.
 *
 * Reconnect: exponential back-off (1 s → 30 s cap). Never auto-enters sim mode;
 *   that is an explicit user choice made in auth.js.
 *
 * Stale detection: if connected but no 'state' message for STALE_MS, warns via
 *   window._showStaleWarning (registered by main.js → ui.js).
 *
 * Outbound commands: sendWsCmd() queues a JSON command on the open socket.
 *   Backend validates with the same guards as REST. Use this from joystick.js.
 *
 * Inbound data: each message type delegates to a window._ hook so this file
 *   has no imports from ui.js/telemetry.js (avoids circular deps).
 */

import { P, EP, loadKey, el, log, setConn } from './config.js';
import { apiFetch }                          from './auth.js';

// ── Constants ─────────────────────────────────────────────────────────────────

const RECONNECT_BASE_MS = 1_000;
const RECONNECT_MAX_MS  = 30_000;
const STALE_MS          = 6_000;

// ── Module state ──────────────────────────────────────────────────────────────

let _reconnectTimer = null;
let _reconnectCount = 0;
let _staleTimer     = null;

// ── Public API ────────────────────────────────────────────────────────────────

export function connectWS() {
  if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null; }

  // Close stale socket if any.
  if (P.ws && P.ws.readyState <= WebSocket.OPEN) { try { P.ws.close(); } catch (_) {} }

  const key    = loadKey();
  const wsBase = P.apiBase.replace(/^http/, 'ws');
  const wsUrl  = key ? `${wsBase}/ws?api_key=${encodeURIComponent(key)}` : `${wsBase}/ws`;

  try { P.ws = new WebSocket(wsUrl); }
  catch (e) { log('err', 'WS init: ' + e.message); _scheduleReconnect(); return; }

  P.ws.onopen = () => {
    _reconnectCount = 0;
    P.wsReconnectAttempts = 0;
    P.connected = true;
    P.simMode   = false;
    setConn('ok', 'Connected');
    el('sim-banner')?.classList.add('hidden');
    log('ok', 'WebSocket connected');
    window._setModeBadge?.('live');
    _resetStaleTimer();
    window.dispatchEvent(new CustomEvent('cerberus:ws-open', { detail: { apiBase: P.apiBase } }));
    _fetchInitialState();
  };

  P.ws.onmessage = e => { try { _route(JSON.parse(e.data)); } catch (_) {} };

  P.ws.onclose = evt => {
    P.connected = false;
    _stopStaleTimer();
    log('warn', `WS closed${evt.reason ? ' (' + evt.reason + ')' : ''} — reconnecting`);
    window.dispatchEvent(new CustomEvent('cerberus:ws-close', { detail: { reason: evt.reason || '' } }));
    _scheduleReconnect();
  };

  P.ws.onerror = () => log('err', 'WS error');
}

/** Send a JSON command over the open socket. Returns false if unavailable. */
export function sendWsCmd(cmd, params = {}) {
  const verification = window.__cerberusControlVerification || null;
  const normalized = String(cmd || '').toLowerCase();
  if (verification?.locked && !['stop', 'estop', 'clear_estop'].includes(normalized)) {
    log('warn', `WS command blocked until live backend verification succeeds: ${cmd}`);
    return false;
  }
  if (!P.ws || P.ws.readyState !== WebSocket.OPEN) return false;
  try { P.ws.send(JSON.stringify({ cmd, ...params })); return true; }
  catch (e) { log('warn', 'WS send: ' + e.message); return false; }
}

/** Called from Settings panel or on API URL change. */
export function reconnectWS() {
  if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null; }
  _reconnectCount = 0;
  if (P.ws) { try { P.ws.close(); } catch (_) {} }
  const key = loadKey();
  if (key) { log('info', 'Reconnecting to ' + P.apiBase); connectWS(); }
  else if (typeof window.showAuthModal === 'function') window.showAuthModal();
}

/** Explicit sim-mode entry — clears any pending reconnect. */
export function enterSimMode() {
  if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null; }
  _reconnectCount = 0;
  P.connected = false;
  P.simMode   = true;
  setConn('warn', 'Simulation');
  window._setModeBadge?.('sim');
  el('sim-banner')?.classList.remove('hidden');
  log('info', 'Simulation mode — no backend required');
  window.dispatchEvent(new CustomEvent('cerberus:sim-mode', { detail: { apiBase: P.apiBase } }));
}

// ── Reconnect scheduler ───────────────────────────────────────────────────────

function _scheduleReconnect() {
  if (_reconnectTimer) return;
  _reconnectCount++;
  P.wsReconnectAttempts = _reconnectCount;
  const delay    = Math.min(RECONNECT_BASE_MS * 2 ** (_reconnectCount - 1), RECONNECT_MAX_MS);
  const delaySec = Math.round(delay / 1000);
  setConn('warn', `Reconnect ×${_reconnectCount} in ${delaySec}s`);
  window._setModeBadge?.('reconnect');
  log('info', `Reconnect ${_reconnectCount} in ${delaySec}s`);
  _reconnectTimer = setTimeout(() => {
    _reconnectTimer = null;
    loadKey() ? connectWS() : enterSimMode();
  }, delay);
}

// ── Stale-data detection ──────────────────────────────────────────────────────

function _resetStaleTimer() {
  _stopStaleTimer();
  _staleTimer = setTimeout(() => {
    if (P.connected) {
      const msg = `No telemetry for ${STALE_MS / 1000}s — EventBus may be stalled`;
      log('warn', msg);
      window._showStaleWarning?.(msg);
    }
  }, STALE_MS);
}

function _stopStaleTimer() {
  if (_staleTimer) { clearTimeout(_staleTimer); _staleTimer = null; }
}

// ── Inbound message router ────────────────────────────────────────────────────

function _route({ type, data, msg, cmd: cmdName }) {
  switch (type) {
    case 'state':
      _resetStaleTimer();
      window._clearStaleWarning?.();
      if (data) _applyState(data);
      break;
    case 'terrain':
      if (data) window._renderTerrainBadge?.(data);
      break;
    case 'stair':
      if (data) { P.stair = data; window._applyStair?.(data); }
      break;
    case 'payload':
      if (data) { P.payload = data; window._applyPayload?.(data); }
      break;
    case 'limb_loss':
      if (data) { P.limbLoss = data; window._applyLimbLoss?.(data); }
      break;
    case 'voice':
      if (data) log('ok', '🎤 ' + (data.transcript || data.intent || JSON.stringify(data)));
      break;
    case 'error':
      log('err', `Backend rejected '${cmdName ?? '?'}': ${msg ?? 'unknown error'}`);
      break;
    case 'ping':
      break;
    default:
      if (P.debug) log('info', `WS [${type}]: ${JSON.stringify(data ?? {}).slice(0, 80)}`);
  }
}

// ── State application (telemetry + estop mirror) ──────────────────────────────

function _applyState(s) {
  if (!s || typeof s !== 'object') return;

  const tel = {
    battery_pct:     s.battery_percent ?? P.telemetry.battery_pct,
    pitch_deg:       (s.pitch  ?? 0) * 180 / Math.PI,
    roll_deg:        (s.roll   ?? 0) * 180 / Math.PI,
    yaw_deg:         (s.yaw    ?? 0) * 180 / Math.PI,
    contact_force_n: s.foot_forces
      ? Object.values(s.foot_forces).reduce((a, b) => a + b, 0) / 4 : 0,
    voltage:         s.battery_voltage ?? P.telemetry.voltage,
    foot_forces:     s.foot_forces     ?? P.telemetry.foot_forces,
    motor_temps:     s.motor_temps     ?? P.telemetry.motor_temps,
    com_x: 0, ctrl_hz: P.telemetry.ctrl_hz,
  };
  window._applyTelemetry?.(tel);

  // Backend is the estop authority — mirror its state.
  if (s.estop_active && !P.estop) {
    P.estop = true;
    const b = el('estop-btn');
    if (b) { b.innerHTML = '✅ Reset'; b.classList.add('fired'); }
    log('err', '!!! Backend reports E-STOP active');
  } else if (!s.estop_active && P.estop) {
    P.estop = false;
    const b = el('estop-btn');
    if (b) { b.innerHTML = '🛑 <span>Stop</span>'; b.classList.remove('fired'); }
  }

  if (s.state) window._applyFSM?.({ state: s.state, armed: P.armed });
}

// ── Initial state bootstrap ───────────────────────────────────────────────────

async function _fetchInitialState() {
  const tryFetch = async (path, cb) => {
    try { const d = await apiFetch(path); if (d) cb(d); }
    catch (_) {}
  };

  await tryFetch(EP.state,   d => _applyState(d));
  await tryFetch(EP.plugins, d => {
    P.plugins = Array.isArray(d) ? d : [];
    window._renderPlugins?.(P.plugins);
  });
  await tryFetch(EP.terrain,  d => { P.terrain = d; window._renderTerrainBadge?.(d); });
  await tryFetch('/session',  d => window._applySession?.(d));
}
