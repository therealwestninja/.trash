/**
 * metrics.js — Observability: metrics grid, health checks, Prometheus,
 * and BT blackboard rendering.
 */

import { P, el, log, fmtDur } from './config.js';
import { apiFetch }            from './api.js';

const _startTime = Date.now();
let _cmdCount    = 0;
let _estopCount  = 0;
let _tripCount   = 0;

export function bumpCmd()   { _cmdCount++; }
export function bumpEstop() { _estopCount++; }
export function bumpTrip()  { _tripCount++; }

// ── Metrics grid ──────────────────────────────────────────────────────────────

export async function loadMetrics() {
  if (P.connected) {
    try {
      const [stats, health] = await Promise.all([
        apiFetch('/stats'),
        apiFetch('/health'),
      ]);
      el('m-uptime')  && (el('m-uptime').textContent = fmtDur(stats.uptime_s || 0));
      el('m-hz')      && (el('m-hz').textContent     = (stats.engine_hz || 0).toFixed(0));
      el('m-cmds')    && (el('m-cmds').textContent   = stats.tick_count || 0);
      _setMVal('m-estops',  _estopCount,  1, 0, v => v);
      _setMVal('m-trips',   _tripCount,   1, 0, v => v);
      _setMVal('m-battery', P.telemetry.battery_pct, 30, 15, v => v.toFixed(0) + '%');
      _setMVal('m-latency', stats.avg_dt_ms || 2.3,  50, 100, v => v.toFixed(1) + 'ms');
      renderHealth(health.checks || []);
    } catch (e) { log('warn', 'Metrics: ' + e.message); }
  } else {
    const uptime = (Date.now() - _startTime) / 1000;
    el('m-uptime')  && (el('m-uptime').textContent = fmtDur(uptime));
    el('m-hz')      && (el('m-hz').textContent     = P.telemetry.ctrl_hz || 500);
    el('m-cmds')    && (el('m-cmds').textContent   = _cmdCount);
    _setMVal('m-estops',  _estopCount,  1, 0, v => v);
    _setMVal('m-trips',   _tripCount,   1, 0, v => v);
    _setMVal('m-battery', P.telemetry.battery_pct || 87, 30, 15, v => v.toFixed(0) + '%');
    _setMVal('m-latency', 2.3, 50, 100, v => v + 'ms');
    renderHealth([
      { name: 'safety',    status: 'ok',      message: 'level=nominal' },
      { name: 'battery',   status: (P.telemetry.battery_pct || 87) > 25 ? 'ok' : 'degraded', message: (P.telemetry.battery_pct || 87).toFixed(0) + '%' },
      { name: 'telemetry', status: 'ok',      message: 'fresh' },
      { name: 'memory',    status: 'ok',      message: '~45 MB' },
    ]);
  }
}

export function renderHealth(checks) {
  const list = el('health-list'); if (!list) return;
  list.innerHTML = checks.map(c => {
    const icon = c.status === 'ok' ? '✅' : c.status === 'degraded' ? '⚠️' : '❌';
    return `<div class="node-row">
      <span class="node-name">${icon} ${c.name}</span>
      <span style="font-size:11px;color:var(--ink3)">${c.message || c.status}</span>
    </div>`;
  }).join('');
}

export async function fetchProm() {
  const pb = el('prom-box'); if (!pb) return;
  if (P.connected) {
    try {
      const r = await fetch(P.apiBase + '/metrics');
      pb.textContent = await r.text();
    } catch (e) { pb.textContent = '// Error: ' + e.message; }
  } else {
    const uptime = ((Date.now() - _startTime) / 1000).toFixed(1);
    pb.textContent = [
      '# CERBERUS Companion — Simulated Metrics',
      `cerberus_uptime_s ${uptime}`,
      `cerberus_battery_pct ${(P.telemetry.battery_pct || 87).toFixed(1)}`,
      `cerberus_engine_hz ${P.telemetry.ctrl_hz || 500}`,
      `cerberus_commands_total ${_cmdCount}`,
      `cerberus_estop_total ${_estopCount}`,
      `cerberus_safety_trips_total ${_tripCount}`,
      `cerberus_pitch_deg ${(P.telemetry.pitch_deg || 0).toFixed(2)}`,
      `cerberus_roll_deg ${(P.telemetry.roll_deg || 0).toFixed(2)}`,
    ].join('\n');
  }
}

// ── Safety events panel ───────────────────────────────────────────────────────

export async function loadSafetyEvents() {
  if (!P.connected) return;
  try {
    const events = await apiFetch('/safety/events');
    P.safety.events = Array.isArray(events) ? events : [];
    renderSafetyEvents();
  } catch (_) {}
}

export function renderSafetyEvents() {
  const list = el('safety-events-list'); if (!list) return;
  const events = P.safety.events.slice(0, 20);
  if (!events.length) { list.innerHTML = '<div style="font-size:11px;color:var(--ink3)">No safety events</div>'; return; }
  const levelColor = { nominal: '#4caf7d', caution: '#e8913a', warning: '#d29922', critical: '#e05a5a', estop: '#8b0000' };
  list.innerHTML = events.map(e => `
    <div class="log-entry">
      <span class="log-ts">${new Date(e.ts * 1000).toTimeString().slice(0, 8)}</span>
      <span class="log-lvl" style="background:${levelColor[e.level] || '#ccc'}11;color:${levelColor[e.level] || '#666'}">${e.level}</span>
      <span class="log-msg">${e.code}: ${e.msg}</span>
    </div>`).join('');
}

// ── BT blackboard ─────────────────────────────────────────────────────────────

export function renderBB() {
  const list = el('bb-list'); if (!list) return;
  const bb = {
    'robot.armed':          P.armed,
    'robot.state':          P.state,
    'robot.battery_pct':    Math.round(P.telemetry.battery_pct || 0),
    'robot.pitch_deg':      Math.round((P.telemetry.pitch_deg || 0) * 10) / 10,
    'robot.roll_deg':       Math.round((P.telemetry.roll_deg  || 0) * 10) / 10,
    'robot.estop':          P.estop,
    'terrain.class':        P.terrain?.terrain_class || 'unknown',
    'perception.human_dist':'~2.0 m',
    'mission.active':       P.missions?.find(m => m.status === 'running')?.id || 'none',
  };
  list.innerHTML = Object.entries(bb).map(([k, v]) => `
    <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--cream)">
      <span style="color:var(--ink3);font-family:var(--mono)">${k}</span>
      <span style="font-weight:500;color:var(--ink)">${v}</span>
    </div>`).join('');
}

// ── Internal helpers ──────────────────────────────────────────────────────────

function _setMVal(id, v, warnAt, errAt, fmt) {
  const e = el(id); if (!e) return;
  e.textContent = typeof fmt === 'function' ? fmt(v) : v;
  e.className   = 'mval '
    + (errAt > 0  && v >= errAt  ? 'err'
    :  warnAt > 0 && v >= warnAt ? 'warn'
    :  'ok');
}
