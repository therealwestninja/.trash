/**
 * config.js — Central state, constants, and tiny shared utilities.
 *
 * Import from this module everywhere else.  Nothing in this file
 * imports from other companion modules — it is the dependency root.
 *
 * Auth model:
 *   • Key stored in sessionStorage (cleared on tab/browser close).
 *   • All API requests inject X-CERBERUS-Key header automatically.
 *   • WebSocket URL appends ?api_key=<key> (browsers can't set WS headers).
 */

// ── Auth key storage ───────────────────────────────────────────────────────────

export const KEY_STORE = 'cerberus_companion_key';
export const loadKey   = () => sessionStorage.getItem(KEY_STORE) || '';
export const saveKey   = k  => sessionStorage.setItem(KEY_STORE, (k || '').trim());

// ── Central mutable state ──────────────────────────────────────────────────────

export const P = {
  connected: false,
  armed: false,
  estop: false,
  simMode: true,
  debug: false,
  ws: null,
  apiBase: 'http://localhost:8080',
  state: 'offline',
  policy: 'SMOOTH',
  locale: 'en',

  /** WS reconnect attempt counter — updated by api.js. */
  wsReconnectAttempts: 0,

  behaviors: [],
  objects: [],
  missions: [],
  logs: [],

  /** CERBERUS plugin roster returned by GET /plugins */
  plugins: [],

  /** ROS 2 / CERBERUS node health rows */
  nodes: [
    { id: 'safety',  name: '/cerberus/safety_watchdog', st: 'ok' },
    { id: 'engine',  name: '/cerberus/core_engine',      st: 'ok' },
    { id: 'bridge',  name: '/cerberus/go2_bridge',       st: 'ok' },
    { id: 'terrain', name: '/cerberus/terrain_arbiter',  st: 'ok' },
    { id: 'stair',   name: '/cerberus/stair_climber',    st: 'ok' },
    { id: 'voice',   name: '/cerberus/voice_nlu',        st: 'ok' },
    { id: 'anatomy', name: '/cerberus/digital_anatomy',  st: 'ok' },
  ],

  telemetry: {
    battery_pct: 87,
    pitch_deg: 0, roll_deg: 0, yaw_deg: 0,
    contact_force_n: 0,
    voltage: 29.4,
    motor_temps: { fl: 42, fr: 43, rl: 41, rr: 42 },
    foot_forces: { fl: 13, fr: 12, rl: 14, rr: 13 },
    com_x: 0,
    ctrl_hz: 500,
  },

  selCat: 'all',
  btBB: {},

  anim: {
    clips: {},
    current: null,
    playing: false,
    speed: 1,
    loop: false,
  },

  i18n: {},
  detections: [],

  /** Terrain classification from the backend TerrainArbiter plugin. */
  terrain: null,

  safety: { level: 'nominal', events: [] },

  /**
   * Latest stair-climber plugin state (populated from WS 'stair' messages).
   * Null until a stair event is received.
   * Shape: { event, status, direction, step, step_count, … }
   */
  stair: null,

  /**
   * Latest payload plugin state (populated from WS 'payload' messages).
   * Null until a payload event is received.
   * Shape: { event, attached, drag_warning, direction, … }
   */
  payload: null,

  /**
   * Latest limb-loss recovery plugin state (populated from WS 'limb_loss' messages).
   * Null until a limb_loss event is received.
   * Shape: { event, limbs_lost, recovered, gait_override, … }
   */
  limbLoss: null,
};

// ── CERBERUS backend endpoint map ──────────────────────────────────────────────

export const EP = {
  root:        '/',
  state:       '/state',
  stats:       '/stats',
  anatomy:     '/anatomy',
  behavior:    '/behavior',
  plugins:     '/plugins',
  safetyEvts:  '/safety/events',
  estop:       '/safety/estop',
  clearEstop:  '/safety/clear_estop',
  standUp:     '/motion/stand_up',
  standDown:   '/motion/stand_down',
  stop:        '/motion/stop',
  move:        '/motion/move',
  bodyHeight:  '/motion/body_height',
  euler:       '/motion/euler',
  gait:        '/motion/gait',
  footRaise:   '/motion/foot_raise',
  sportMode:   '/motion/sport_mode',
  led:         '/led',
  terrain:     '/terrain',
  health:      '/health',
  ready:       '/ready',
  session:     '/session',
  stair:       '/stair',
  limbLoss:    '/limb_loss',
  payload:     '/payload',
  voice:       '/voice',
  goalPost:    '/behavior/goal',
};

// Companion UI behavior-id → CERBERUS SportMode string
export const BEHAVIOR_TO_SPORT = {
  sit:         'sit',
  stand:       'stand_up',
  stretch:     'stretch',
  head_tilt:   'hello',
  tail_wag:    'dance1',
  roll_over:   'wallow',
  paw_shake:   'scrape',
  zoomies:     'dance2',
  play_bow:    'balance_stand',
  idle_breath: 'balance_stand',
  follow:      'balance_stand',
};

// ── Tiny utilities (no side-effects) ──────────────────────────────────────────

/** Get element by id — used everywhere. */
export const el = id => document.getElementById(id);

/** Log entry pushed into P.logs and rendered. */
export function log(lvl, msg) {
  const ts = new Date().toTimeString().slice(0, 8);
  P.logs.unshift({ ts, lvl, msg: String(msg) });
  if (P.logs.length > 300) P.logs.pop();
  renderLogImpl();
}

/** Inner render — called by log() and by the clear button. */
export function renderLogImpl() {
  const list = el('log-list');
  if (!list) return;
  list.innerHTML = P.logs.slice(0, 80).map(e =>
    `<div class="log-entry">
       <span class="log-ts">${e.ts}</span>
       <span class="log-lvl ${e.lvl}">${e.lvl}</span>
       <span class="log-msg">${_escHtml(e.msg)}</span>
     </div>`
  ).join('');
}

/** Update connection indicator. */
export function setConn(cls, txt) {
  const d = el('conn-dot');
  if (d) d.className = 'dot ' + cls;
  const t = el('conn-txt');
  if (t) t.textContent = txt;
}

/** Format duration in seconds to "1h 2m 3s" etc. */
export function fmtDur(s) {
  if (s < 60)   return Math.round(s) + 's';
  if (s < 3600) return Math.floor(s / 60) + 'm ' + Math.round(s % 60) + 's';
  return Math.floor(s / 3600) + 'h ' + Math.floor((s % 3600) / 60) + 'm';
}

/**
 * Escape HTML special characters before injecting any externally sourced
 * strings into innerHTML.  Used for log messages.
 */
function _escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
