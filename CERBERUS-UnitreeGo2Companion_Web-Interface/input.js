/**
 * input.js — Unified input manager for CERBERUS Companion.
 *
 * Merges keyboard, gamepad, and virtual joystick input into one normalized
 * command stream. Designed to be controller-safe and plugin-friendly.
 */

const STORAGE_KEY = 'cerberus_input_settings_v1';

const DEFAULT_BINDINGS = {
  forward: ['KeyW', 'ArrowUp'],
  back: ['KeyS', 'ArrowDown'],
  left: ['KeyA', 'ArrowLeft'],
  right: ['KeyD', 'ArrowRight'],
  yawLeft: ['KeyQ'],
  yawRight: ['KeyE'],
  boost: ['ShiftLeft', 'ShiftRight'],
  precision: ['ControlLeft', 'ControlRight'],
  stop: ['Space'],
  stand: ['Digit1'],
  sit: ['Digit2'],
  arm: ['KeyR'],
  heightUp: ['PageUp'],
  heightDown: ['PageDown'],
  estop: ['Escape'],
};

const ACTION_LABELS = {
  forward: 'Forward', back: 'Backward', left: 'Strafe Left', right: 'Strafe Right',
  yawLeft: 'Yaw Left', yawRight: 'Yaw Right', boost: 'Speed Boost', precision: 'Precision Mode',
  stop: 'Stop', stand: 'Stand', sit: 'Sit', arm: 'Arm / Disarm',
  heightUp: 'Body Height Up', heightDown: 'Body Height Down', estop: 'E-STOP',
};

const state = {
  activeDevice: 'none',
  keysDown: new Set(),
  joystickL: { x: 0, y: 0 },
  joystickR: { x: 0, y: 0 },
  gamepadConnected: false,
  gamepadIndex: null,
  reducedMotion: false,
  deadZone: 0.12,
  sensitivity: 'square',
  maxSpeed: 1.0,
  commandHz: 10,
  bindings: structuredClone(DEFAULT_BINDINGS),
  lastDigitalActionAt: 0,
  timer: null,
};

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const d = JSON.parse(raw);
    if (typeof d !== 'object' || !d) return;
    state.reducedMotion = !!d.reducedMotion;
    state.deadZone = clamp(Number(d.deadZone ?? state.deadZone), 0, 0.4);
    state.sensitivity = ['linear','square','cube'].includes(d.sensitivity) ? d.sensitivity : state.sensitivity;
    state.maxSpeed = clamp(Number(d.maxSpeed ?? state.maxSpeed), 0.1, 2.0);
    state.commandHz = clamp(Number(d.commandHz ?? state.commandHz), 1, 50);
    if (d.bindings && typeof d.bindings === 'object') {
      for (const [k, v] of Object.entries(DEFAULT_BINDINGS)) {
        if (Array.isArray(d.bindings[k])) state.bindings[k] = d.bindings[k].map(String);
      }
    }
  } catch {}
}

function saveSettings() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    reducedMotion: state.reducedMotion,
    deadZone: state.deadZone,
    sensitivity: state.sensitivity,
    maxSpeed: state.maxSpeed,
    commandHz: state.commandHz,
    bindings: state.bindings,
  }));
}

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function applyDeadZone(v) {
  const a = Math.abs(v);
  if (a <= state.deadZone) return 0;
  const scaled = (a - state.deadZone) / (1 - state.deadZone);
  return Math.sign(v) * scaled;
}

function curve(v) {
  if (v === 0) return 0;
  const s = Math.sign(v);
  const a = Math.abs(v);
  if (state.sensitivity === 'linear') return v;
  if (state.sensitivity === 'cube') return s * a * a * a;
  return s * a * a;
}

function effectiveSpeed() {
  let speed = state.maxSpeed;
  if (isPressed('boost')) speed *= 1.8;
  if (isPressed('precision')) speed *= 0.3;
  if (state.reducedMotion) speed *= 0.5;
  return clamp(speed, 0.1, 2.0);
}

function isPressed(action) {
  const keys = state.bindings[action] || [];
  return keys.some(k => state.keysDown.has(k));
}

function focusedEditable(el) {
  if (!el) return false;
  const tag = (el.tagName || '').toLowerCase();
  return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
}

function digitalAxis(posAction, negAction) {
  let v = 0;
  if (isPressed(posAction)) v += 1;
  if (isPressed(negAction)) v -= 1;
  return v;
}

function computeKeyboardCommand() {
  const vx = digitalAxis('forward', 'back');
  const vy = digitalAxis('right', 'left');
  const vyaw = digitalAxis('yawRight', 'yawLeft');
  return { vx, vy, vyaw, speed: effectiveSpeed(), source: 'keyboard' };
}

function getGamepadCommand() {
  const pads = navigator.getGamepads?.() || [];
  const gp = pads[state.gamepadIndex ?? 0];
  if (!gp) return null;
  state.gamepadConnected = true;
  const lx = curve(applyDeadZone(gp.axes[0] || 0));
  const ly = curve(applyDeadZone(gp.axes[1] || 0));
  const rx = curve(applyDeadZone(gp.axes[2] || 0));
  const lt = gp.buttons?.[6]?.value || 0;
  const rt = gp.buttons?.[7]?.value || 0;
  let speed = state.maxSpeed * (1 + rt * 0.8);
  if (lt > 0.2) speed *= 0.3;
  if (state.reducedMotion) speed *= 0.5;
  const action = gp.buttons?.[0]?.pressed ? 'stand'
    : gp.buttons?.[3]?.pressed ? 'sit'
    : (gp.buttons?.[4]?.pressed && gp.buttons?.[5]?.pressed && gp.buttons?.[1]?.pressed) ? 'estop'
    : gp.buttons?.[12]?.pressed ? 'height_up'
    : gp.buttons?.[13]?.pressed ? 'height_dn'
    : null;
  return { vx: -ly, vy: lx, vyaw: rx, speed: clamp(speed,0.1,2.0), source: 'gamepad', action };
}

function getJoystickCommand() {
  const lx = curve(applyDeadZone(state.joystickL.x));
  const ly = curve(applyDeadZone(state.joystickL.y));
  const rx = curve(applyDeadZone(state.joystickR.x));
  return { vx: -ly, vy: lx, vyaw: rx, speed: effectiveSpeed(), source: 'joystick' };
}

function chooseCommand() {
  const gamepad = getGamepadCommand();
  const joystick = getJoystickCommand();
  const keyboard = computeKeyboardCommand();

  const hasMove = c => c && (Math.abs(c.vx) > 0.01 || Math.abs(c.vy) > 0.01 || Math.abs(c.vyaw) > 0.01);
  if (gamepad && (hasMove(gamepad) || gamepad.action)) return gamepad;
  if (hasMove(joystick)) return joystick;
  if (hasMove(keyboard)) return keyboard;

  if (isPressed('stop')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'stop' };
  if (isPressed('stand')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'stand' };
  if (isPressed('sit')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'sit' };
  if (isPressed('arm')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'arm' };
  if (isPressed('heightUp')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'height_up' };
  if (isPressed('heightDown')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'height_dn' };
  if (isPressed('estop')) return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'keyboard', action: 'estop' };
  return { vx: 0, vy: 0, vyaw: 0, speed: effectiveSpeed(), source: 'none' };
}

function dispatchLoop() {
  const cmd = chooseCommand();
  state.activeDevice = cmd.source || 'none';
  updateIndicators();
  window._inputDispatch?.(cmd);
}

function resetLoop() {
  if (state.timer) clearInterval(state.timer);
  state.timer = setInterval(dispatchLoop, Math.max(20, Math.round(1000 / state.commandHz)));
}

function updateIndicators() {
  const map = { none: '— none', keyboard: '⌨ keyboard', gamepad: '🎮 gamepad', joystick: '🕹 joystick' };
  document.getElementById('input-device-indicator')?.replaceChildren(document.createTextNode(map[state.activeDevice] || state.activeDevice));
}

function renderBindings() {
  const root = document.getElementById('input-bindings-list');
  if (!root) return;
  root.innerHTML = '';
  Object.entries(ACTION_LABELS).forEach(([action, label]) => {
    const row = document.createElement('div');
    row.className = 'input-binding-row';
    const keys = (state.bindings[action] || []).map(k => `<span class="key-chip">${k}</span>`).join('');
    row.innerHTML = `
      <div class="input-binding-action">${label}</div>
      <div class="input-binding-keys">${keys || '<span style="font-size:11px;color:var(--ink3)">—</span>'}</div>
      <button class="fs-btn-xs" data-action="remap">Remap</button>
      <button class="fs-btn-xs danger" data-action="clear">Clear</button>`;
    row.querySelector('[data-action="remap"]').addEventListener('click', () => {
      const cur = (state.bindings[action] || []).join(', ');
      const raw = prompt(`Enter comma-separated key codes for ${label}`, cur);
      if (raw == null) return;
      state.bindings[action] = raw.split(',').map(s => s.trim()).filter(Boolean);
      saveSettings();
      renderBindings();
    });
    row.querySelector('[data-action="clear"]').addEventListener('click', () => {
      state.bindings[action] = [];
      saveSettings();
      renderBindings();
    });
    root.appendChild(row);
  });
}

function bindSettingsControls() {
  const reduced = document.getElementById('input-reduced-motion-toggle');
  if (reduced) {
    reduced.checked = state.reducedMotion;
    reduced.addEventListener('change', e => { state.reducedMotion = !!e.target.checked; saveSettings(); });
    const mq = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    if (mq?.matches && !localStorage.getItem(STORAGE_KEY)) reduced.checked = state.reducedMotion = true;
  }
  const dz = document.getElementById('input-dead-zone');
  const dzv = document.getElementById('input-dead-zone-val');
  if (dz) {
    dz.value = String(state.deadZone);
    dzv && (dzv.textContent = state.deadZone.toFixed(2));
    dz.addEventListener('input', e => { state.deadZone = clamp(Number(e.target.value), 0, 0.4); saveSettings(); if (dzv) dzv.textContent = state.deadZone.toFixed(2); });
  }
  const sens = document.getElementById('input-sensitivity');
  if (sens) { sens.value = state.sensitivity; sens.addEventListener('change', e => { state.sensitivity = e.target.value; saveSettings(); }); }
  const maxSp = document.getElementById('input-max-speed');
  if (maxSp) { maxSp.value = String(state.maxSpeed); maxSp.addEventListener('change', e => { state.maxSpeed = clamp(Number(e.target.value), 0.1, 2.0); saveSettings(); }); }
  const hz = document.getElementById('input-command-hz');
  if (hz) { hz.value = String(state.commandHz); hz.addEventListener('change', e => { state.commandHz = clamp(Number(e.target.value), 1, 50); saveSettings(); resetLoop(); }); }
  document.getElementById('input-reset-bindings')?.addEventListener('click', () => {
    state.bindings = structuredClone(DEFAULT_BINDINGS);
    saveSettings();
    renderBindings();
  });
}

function onKeyDown(e) {
  if (focusedEditable(e.target)) return;
  state.keysDown.add(e.code);
  if (['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','PageUp','PageDown'].includes(e.code)) e.preventDefault();
}

function onKeyUp(e) {
  state.keysDown.delete(e.code);
}

function onGamepadConnected(e) {
  state.gamepadConnected = true;
  state.gamepadIndex = e.gamepad?.index ?? 0;
  window._showToast?.(`Gamepad connected: ${e.gamepad?.id || 'controller'}`, 'ok');
}

function onGamepadDisconnected() {
  state.gamepadConnected = false;
  state.gamepadIndex = null;
}

export function initInput() {
  loadSettings();
  bindSettingsControls();
  renderBindings();
  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);
  window.addEventListener('gamepadconnected', onGamepadConnected);
  window.addEventListener('gamepaddisconnected', onGamepadDisconnected);
  window._inputSetJoystickL = (x, y) => { state.joystickL = { x: clamp(Number(x)||0,-1,1), y: clamp(Number(y)||0,-1,1) }; };
  window._inputSetJoystickR = (x, y) => { state.joystickR = { x: clamp(Number(x)||0,-1,1), y: clamp(Number(y)||0,-1,1) }; };
  window._inputGetActiveDevice = () => state.activeDevice;
  resetLoop();
  updateIndicators();
}
