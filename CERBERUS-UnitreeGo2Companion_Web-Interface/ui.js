/**
 * ui.js — Operator control surface: estop, arm, nav, nodes, BT, safety,
 *          terrain badge, stale-data overlay, theme, body controls.
 *
 * What was here and is now elsewhere:
 *   applyTelemetry → telemetry.js
 *   applyFSM       → fsm.js
 *   initJoystick   → joystick.js
 *   applyPayload,
 *   applyLimbLoss,
 *   applyStair     → plugin-status.js
 */

import { P, el, log }       from './config.js';
import { apiCmd, apiPost,
         apiFetch,
         enterSimMode }      from './api.js';
import { EP }                from './config.js';
import { drawBT }            from './canvas.js';
import { renderBB }          from './metrics.js';

// ── Stale-data overlay ────────────────────────────────────────────────────────

/** Called by ws.js via window._showStaleWarning. */
export function showStaleWarning(msg) {
  const d = el('conn-dot');  if (d) { d.className = 'dot warn'; }
  const t = el('conn-txt');  if (t) { t.textContent = '⚠ Stale'; t.title = msg; }
}

/** Called by ws.js via window._clearStaleWarning. */
export function clearStaleWarning() {
  const t = el('conn-txt'); if (t) t.title = '';
}

/**
 * setModeBadge — update the header SIM/LIVE indicator.
 * Call with ('sim') or ('live') or ('reconnect').
 * Registered on window._setModeBadge by main.js.
 */
export function setModeBadge(mode) {
  const b = el('mode-badge'); if (!b) return;
  const map = {
    sim:       { txt: 'SIM',        cls: '' },
    live:      { txt: 'LIVE',       cls: 'live' },
    reconnect: { txt: 'RECONNECT',  cls: 'warn' },
  };
  const m = map[mode] || map.sim;
  b.textContent = m.txt;
  b.className   = 'mode-badge' + (m.cls ? ' ' + m.cls : '');
}

// ── Terrain badge ─────────────────────────────────────────────────────────────

export function renderTerrainBadge(data) {
  const b = el('terrain-badge'); if (!b || !data) return;
  const cls = (data.terrain_class || 'unknown').toLowerCase();
  b.textContent   = '⛰ ' + (data.terrain_class || '—');
  b.className     = `terrain-chip terrain-${cls}`;
  b.style.display = 'inline-flex';
}

// ── E-STOP ────────────────────────────────────────────────────────────────────

export async function triggerEstop() {
  if (P.estop) {
    P.estop = false;
    _setEstopBtn(false);
    await apiCmd('CLEAR_ESTOP');
    log('warn', 'E-STOP cleared — re-arm before operating');
  } else {
    P.estop = true;
    _setEstopBtn(true);
    await apiCmd('ESTOP');
    log('err', '!!! E-STOP triggered');
  }
}

function _setEstopBtn(fired) {
  const b = el('estop-btn'); if (!b) return;
  b.innerHTML = fired ? '✅ Reset' : '🛑 <span>Stop</span>';
  b.classList.toggle('fired', fired);
}

// ── ARM ───────────────────────────────────────────────────────────────────────

export async function toggleArm() {
  if (P.estop) { log('err', 'Cannot arm — E-STOP active'); return; }
  P.armed = !P.armed;
  await apiCmd(P.armed ? 'ARM' : 'DISARM');
  _setArmBtn(P.armed);
}

function _setArmBtn(armed) {
  const b = el('arm-btn'); if (!b) return;
  const ico = el('arm-ico'); if (ico) ico.textContent = armed ? '🔓' : '🔒';
  const txt = el('arm-txt'); if (txt) txt.textContent = armed ? 'Armed' : 'Arm';
  b.className = 'arm-btn' + (armed ? ' armed' : '');
}

// ── Body controls (passthrough from HTML sliders/buttons) ────────────────────

export function cmd(action) { apiCmd(action); }

export function bctrl(param, val) {
  const ids = { height: 'bc-h', roll: 'bc-r', yaw: 'bc-y', speed: 'bc-s' };
  const fmt = { height: v => (+v).toFixed(2) + 'm', roll: v => Math.round(+v) + '°',
                yaw: v => Math.round(+v) + '°',      speed: v => (+v).toFixed(1) + 'm/s' };
  const e = el(ids[param]); if (e) e.textContent = fmt[param](val);
  apiCmd('BODY_CTRL', { [param]: val });
}

export async function setPolicy(name, polEl) {
  P.policy = name;
  document.querySelectorAll('.pol-opt').forEach(e => e.classList.remove('active'));
  if (polEl) polEl.classList.add('active');
  await apiCmd('SET_POLICY', { policy: name });
  log('ok', 'Policy: ' + name);
}

// ── Node health list ──────────────────────────────────────────────────────────

export function renderNodes() {
  const list = el('nodes-list'); if (!list) return;
  list.innerHTML = P.nodes.map(n =>
    `<div class="node-row">
       <span class="node-name">${n.name}</span>
       <span class="nst ${n.st}">${n.st}</span>
     </div>`
  ).join('');
}

// ── Tab navigation ────────────────────────────────────────────────────────────

export function goTab(name, navEl) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav') .forEach(n => n.classList.remove('active'));
  el('tab-' + name)?.classList.add('active');
  navEl?.classList.add('active');

  // Tab-specific refresh — use window.* to avoid importing every sub-module.
  const refresh = {
    tricks:   () => window.renderBehaviors?.(),
    objects:  () => window.renderObjects?.(),
    missions: () => window.renderMissions?.(),
    settings: () => window.renderLangGrid?.(),
    metrics:  () => window.loadMetrics?.(),
    bt:           () => { drawBT(); renderBB(); },
    funscript:    () => window.renderFunScriptUI?.(),
    diagnostics:  () => window.renderDiagnosticsUI?.(),
    anim:     () => window.renderAnimClipList?.(),
  };
  refresh[name]?.();
}

export function rpTab(name, tabEl) {
  document.querySelectorAll('.rptab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.rpsec').forEach(s => s.classList.remove('active'));
  tabEl?.classList.add('active');
  el('rps-' + name)?.classList.add('active');
}

export function openMin()   { el('minover')?.classList.add('open');    }
export function closeMin()  { el('minover')?.classList.remove('open'); }
export function setTheme(v) { log('info', 'Theme: ' + v); }

// ── BT controls ───────────────────────────────────────────────────────────────

export async function btCmd(action) {
  if (P.connected) {
    try {
      await apiPost('/api/v1/bt/' + action);
      const s = await apiFetch('/api/v1/bt/status');
      const st = el('bt-status');
      if (st) st.textContent = `Status: ${s.last_status} · ticks: ${s.ticks}`;
    } catch (e) { log('err', 'BT: ' + e.message); }
  } else {
    const st = el('bt-status');
    if (st) st.textContent = `Status: ${action} (simulation)`;
    log('ok', 'BT ' + action + ' (sim)');
  }
}

// ── Safety thresholds ─────────────────────────────────────────────────────────

export async function updateThresh(type, val) {
  const ids = { pitch: 'th-pitch', roll: 'th-roll', force: 'th-force' };
  const fmt = { pitch: v => v + '°', roll: v => v + '°', force: v => v + 'N' };
  const e = el(ids[type]); if (e) e.textContent = fmt[type](val);
  if (P.connected) {
    const keys = { pitch: 'pitch_limit_deg', roll: 'roll_limit_deg', force: 'force_limit_n' };
    try { await apiPost('/api/v1/safety/config', { [keys[type]]: val }); } catch (_) {}
  }
  log('warn', `Safety ${type} → ${fmt[type](val)}`);
}

// ── Re-export so html onclick="window.enterSimMode()" works ──────────────────
export { enterSimMode };
