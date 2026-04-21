/**
 * telemetry.js — Apply incoming telemetry to DOM elements.
 *
 * Single responsibility: map a telemetry object to DOM updates.
 * Does not know where the data came from (WS, sim loop, or otherwise).
 * Registered on window._applyTelemetry by main.js.
 */

import { P, el } from './config.js';
import { drawRobot } from './canvas.js';

export function applyTelemetry(tel) {
  if (!tel) return;
  P.telemetry = { ...P.telemetry, ...tel };

  // Battery bar + colour
  const bp = Math.round(tel.battery_pct || 0);
  const bc = bp > 30 ? 'var(--leaf)' : bp > 15 ? 'var(--amber)' : 'var(--rose)';
  _set('bat-fill',   e => { e.style.width = bp + '%'; e.style.background = bc; });
  _set('bat-pct',    e => e.textContent = bp + '%');
  _set('vc-bat',     e => e.style.background = bc);
  _set('vc-bat-txt', e => e.textContent = 'Battery ' + bp + '%');

  // Gauge cells: value, warn threshold, error threshold, format fn
  const gauges = [
    ['t-pitch', tel.pitch_deg || 0,       6,   10,  v => (v >= 0 ? '+' : '') + v.toFixed(1) + '°'],
    ['t-roll',  tel.roll_deg  || 0,       6,   10,  v => (v >= 0 ? '+' : '') + v.toFixed(1) + '°'],
    ['t-force', tel.contact_force_n || 0, 20,  30,  v => Math.round(v) + 'N'],
    ['r-pitch', tel.pitch_deg || 0,       6,   10,  v => v.toFixed(1) + '°'],
    ['r-roll',  tel.roll_deg  || 0,       6,   10,  v => v.toFixed(1) + '°'],
    ['r-cf',    tel.contact_force_n || 0, 20,  30,  v => Math.round(v) + 'N'],
    ['t-hz',    tel.ctrl_hz   || 500,     490, 450, v => Math.round(v)],
  ];
  for (const [id, v, wHi, eHi, fmt] of gauges) {
    _set(id, e => {
      e.textContent = fmt(v);
      e.className   = 'tval ' + (Math.abs(v) >= eHi ? 'err' : Math.abs(v) >= wHi ? 'warn' : 'ok');
    });
  }

  _set('r-yaw',  e => e.textContent = (tel.yaw_deg  || 0).toFixed(1) + '°');
  _set('r-volt', e => e.textContent = (tel.voltage   || 0).toFixed(1) + 'V');
  _set('r-hz',   e => e.textContent = Math.round(tel.ctrl_hz || 500));

  // Foot forces
  const ff = tel.foot_forces || {};
  ['fl','fr','rl','rr'].forEach(k => _set('r-' + k, e => e.textContent = Math.round(ff[k] || 0)));

  // Motor temps
  const mt = tel.motor_temps || {};
  ['fl','fr','rl','rr'].forEach(k => {
    _set('r-t' + k, e => {
      const v = Math.round(mt[k] || 0);
      e.textContent = v + '°';
      e.className   = 'tval ' + (v > 72 ? 'err' : v > 58 ? 'warn' : 'ok');
    });
  });

  // IMU vitals chip
  const p = tel.pitch_deg || 0, r = tel.roll_deg || 0;
  const imuOk = Math.abs(p) < 6 && Math.abs(r) < 6;
  const imuCls = imuOk ? 'var(--leaf)' : (Math.abs(p) > 9 || Math.abs(r) > 9) ? 'var(--rose)' : 'var(--amber)';
  _set('vc-imu',     e => e.style.background = imuCls);
  _set('vc-imu-txt', e => e.textContent = imuOk ? 'IMU balanced' : `Pitch ${p.toFixed(1)}°`);

  drawRobot(P.telemetry);
}

/** Null-safe element accessor + updater. */
function _set(id, fn) { const e = el(id); if (e) fn(e); }
