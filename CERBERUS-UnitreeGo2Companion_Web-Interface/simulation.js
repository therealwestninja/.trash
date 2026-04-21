/**
 * simulation.js — Browser-side simulation loop.
 *
 * Generates plausible telemetry when no backend is reachable, keeping the
 * UI fully interactive as a demo/dev unit. Also drives simulated plugin
 * events (terrain, stair, payload, limb_loss) so plugin-status.js can be
 * exercised offline.
 *
 * simCmd() drives FSM transitions.
 * startSimLoop() / stopSimLoop() control the tick timer.
 */

import { P, log } from './config.js';

// ── Constants ─────────────────────────────────────────────────────────────────

const SIM_HZ       = 20;
const SIM_INTERVAL = 1000 / SIM_HZ;

// ── Module state ──────────────────────────────────────────────────────────────

let _simT0    = Date.now();
let _simFrame = 0;
let _simTimer = null;

// ── FSM maps ──────────────────────────────────────────────────────────────────

const ACTION_STATE = {
  STAND: 'standing', SIT: 'sitting', WALK: 'walking',
  FOLLOW: 'following', NAVIGATE: 'navigating',
  INTERACT: 'interacting', PERFORM: 'performing', RUN_BEHAVIOR: 'performing',
};

const SPORT_STATE = {
  stand_up: 'standing', sit: 'sitting',
  wallow: 'performing', dance1: 'performing', dance2: 'performing',
  hello: 'performing', stretch: 'performing', scrape: 'performing',
  balance_stand: 'standing',
};

// ── Public API ────────────────────────────────────────────────────────────────

export function simCmd(action, params = {}) {
  const next = ACTION_STATE[action];
  if (next) { P.state = next; _pushFSM(); }

  if (action === 'ARM')         { P.armed = true;  _pushFSM(); }
  if (action === 'DISARM')      { P.armed = false; _pushFSM(); }
  if (action === 'ESTOP')       { P.estop = true;  P.state = 'estop'; _pushFSM(); }
  if (action === 'CLEAR_ESTOP') { P.estop = false; P.state = 'idle';  _pushFSM(); }

  if (action === 'SPORT_MODE' && params.mode) {
    P.state = SPORT_STATE[params.mode] ?? 'performing';
    _pushFSM();
    const TRICKS = ['wallow','dance1','dance2','hello','stretch','scrape'];
    if (TRICKS.includes(params.mode))
      setTimeout(() => { P.state = 'standing'; _pushFSM(); log('ok', 'Behavior complete'); }, 3000);
  }

  if (action === 'RUN_BEHAVIOR' && params.behavior_id) {
    P.state = 'performing';
    _pushFSM();
    const b   = P.behaviors.find(b => b.id === params.behavior_id);
    const dur = (b?.duration_s ?? 2) * 1000;
    setTimeout(() => {
      P.state = 'standing';
      _pushFSM();
      log('ok', 'Behavior complete: ' + (b?.name ?? params.behavior_id));
    }, dur);
  }
}

export function startSimLoop() {
  if (_simTimer) return;
  _simT0    = Date.now();
  _simFrame = 0;
  _simTimer = setInterval(_tick, SIM_INTERVAL);
  log('info', `Simulation loop ${SIM_HZ} Hz`);
}

export function stopSimLoop() {
  if (_simTimer) { clearInterval(_simTimer); _simTimer = null; }
}

// ── Tick ──────────────────────────────────────────────────────────────────────

function _tick() {
  _simFrame++;
  const t      = (Date.now() - _simT0) / 1000;
  const active = ['performing','interacting','walking','following','navigating','patrolling']
    .includes(P.state);
  const n = (freq, lo, hi) =>
    lo + (Math.sin(t * freq + Math.cos(t * 0.7) * 0.3) * 0.5 + 0.5) * (hi - lo);

  // Telemetry
  window._applyTelemetry?.({
    battery_pct:    Math.max(5, 87 - t * 0.003),
    voltage:        29.4 - t * 0.0002,
    pitch_deg:      Math.sin(t * 1.7) * (active ? 2.5 : 0.5),
    roll_deg:       Math.sin(t * 2.3) * (active ? 1.2 : 0.3),
    yaw_deg:        (t * 8) % 360,
    contact_force_n: active ? Math.max(0, Math.sin(t * 3.2) * 10 + 5) : 0,
    com_x:          Math.sin(t * 0.7) * 0.03,
    ctrl_hz:        active ? 498 + Math.round(n(3, 0, 4)) : 500,
    foot_forces:  { fl: n(2.1, 10, 18), fr: n(1.7, 10, 18), rl: n(2.5, 10, 18), rr: n(2.9, 10, 18) },
    motor_temps:  { fl: n(0.3, 40, 44), fr: n(0.5, 41, 45), rl: n(0.4, 40, 44), rr: n(0.6, 41, 45) },
  });

  // Occasional node health flicker (not safety node).
  if (Math.random() < 0.002) {
    const node = P.nodes.filter(n => n.id !== 'safety')[Math.floor(Math.random() * (P.nodes.length - 1))];
    if (node) {
      node.st = 'warn';
      setTimeout(() => { node.st = 'ok'; }, 2500 + Math.random() * 2000);
    }
  }

  // Terrain rotation every 5 s.
  if (_simFrame % (SIM_HZ * 5) === 0) {
    const classes = ['FLAT','ROUGH','SOFT','INCLINE_UP','INCLINE_DOWN','LATERAL_SLOPE'];
    P.terrain = { terrain_class: classes[Math.floor(Math.random() * classes.length)], confidence: 0.8 + Math.random() * 0.2 };
    window._renderTerrainBadge?.(P.terrain);
  }

  // Stair event — once every 30 s.
  if (_simFrame === SIM_HZ * 30) {
    const stairEvt = { event: 'stair.detected', direction: 'UP', step_count: 4 };
    window._applyStair?.(stairEvt);
    setTimeout(() => window._applyStair?.({ event: 'stair.exited' }), 8000);
  }

  // Payload event — once every 45 s.
  if (_simFrame === SIM_HZ * 45) {
    window._applyPayload?.({ event: 'payload.attached', attached: true });
    setTimeout(() => window._applyPayload?.({ event: 'payload.drag_warning', drag_warning: true, direction: 'LEFT' }), 3000);
    setTimeout(() => window._applyPayload?.({ event: 'payload.detached', attached: false }), 9000);
  }

  // Limb-loss event — once every 60 s.
  if (_simFrame === SIM_HZ * 60) {
    window._applyLimbLoss?.({ event: 'limb_loss.detected', limbs_lost: ['FR'] });
    setTimeout(() => window._applyLimbLoss?.({ event: 'limb_loss.cleared', recovered: true, limbs_lost: [] }), 10000);
  }

  // Animation tick.
  window._animTick?.(t);

  // BT update every 300 ms.
  if (_simFrame % Math.round(300 / SIM_INTERVAL) === 0)
    window._simulateBT?.();
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function _pushFSM() {
  window._applyFSM?.({ state: P.state, armed: P.armed });
}

// ── Built-in seed data ────────────────────────────────────────────────────────

export function loadBuiltinBehaviors() {
  P.behaviors = [
    { id: 'sit',         name: 'Sit',        category: 'posture',   icon: '🐾', duration_s: 1.5 },
    { id: 'stand',       name: 'Stand',       category: 'posture',   icon: '🐕', duration_s: 1.2 },
    { id: 'stretch',     name: 'Stretch',     category: 'posture',   icon: '🐶', duration_s: 2.0 },
    { id: 'head_tilt',   name: 'Head Tilt',   category: 'express',   icon: '🤔', duration_s: 1.0 },
    { id: 'tail_wag',    name: 'Happy Wag',   category: 'express',   icon: '🎉', duration_s: 2.5 },
    { id: 'roll_over',   name: 'Roll Over',   category: 'trick',     icon: '🔄', duration_s: 3.0 },
    { id: 'paw_shake',   name: 'Shake Paw',   category: 'trick',     icon: '🤝', duration_s: 2.0 },
    { id: 'zoomies',     name: 'Zoomies!',    category: 'play',      icon: '💨', duration_s: 4.0 },
    { id: 'play_bow',    name: 'Play Bow',    category: 'play',      icon: '🙇', duration_s: 1.5 },
    { id: 'follow',      name: 'Follow Me',   category: 'companion', icon: '👣' },
    { id: 'patrol',      name: 'Patrol',      category: 'mission',   icon: '🗺️' },
    { id: 'idle_breath', name: 'Breathing',   category: 'idle',      icon: '💤' },
  ];
}

export function loadBuiltinObjects() {
  P.objects = [
    { id: 'cushion_blue', name: 'Blue Cushion', type: 'soft_prop',  affordances: ['mount_play','knead'], moods: ['playful'],      max_force_n: 20 },
    { id: 'chair1',       name: 'Wooden Chair', type: 'hard_prop',  affordances: ['scratch','shake'],    moods: ['excited'],      max_force_n: 30 },
    { id: 'plush_dog',    name: 'Plush Dog',    type: 'soft_prop',  affordances: ['nuzzle','knead'],     moods: ['affectionate'], max_force_n: 15 },
  ];
}

export function loadBuiltinMissions() {
  P.missions = [
    { id: '1', name: 'Home Patrol', type: 'patrol', status: 'pending', progress: 0 },
  ];
}
