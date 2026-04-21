import { P, el, loadKey, log } from './config.js';
import { connectWS, reconnectWS, enterSimMode } from './ws.js';
import { showAuthModal } from './auth.js';

const PROFILE_STORE = 'cerberus_control_profile_v1';
const VERIFY_TIMEOUT_MS = 1800;

const PROFILES = {
  localhost: {
    id: 'localhost',
    label: 'LocalHost / Demo',
    shortLabel: 'LocalHost',
    badgeTone: 'terrain-soft',
    modeBadge: 'SIM PREF',
    description: 'Browser-local demo and simulation surface. Safe default when no CERBERUS-backed Go2 is connected.',
    bannerTitle: '⚡ LocalHost / Demo profile active.',
    bannerDesc: 'Browser simulation is enabled by default. You can still connect to a backend manually for local testing.',
    connectionSummary: 'LocalHost prefers safe demo/simulation mode. Connect only when you want to test against a reachable CERBERUS backend.',
    authCopy: 'Leave blank to stay in <strong>browser simulation mode</strong> for local demo and validation.',
    defaultApiBase: 'http://localhost:8080',
    preferSim: true,
    requireKeyPrompt: false,
    connectButton: 'Connect Local Test Backend',
  },
  pythonserver: {
    id: 'pythonserver',
    label: 'PythonServer / Go2',
    shortLabel: 'PythonServer',
    badgeTone: 'terrain-flat',
    modeBadge: 'LIVE PREF',
    description: 'Operator-facing control surface for a Unitree Go2 running the CERBERUS Python backend.',
    bannerTitle: '🛰️ PythonServer / Go2 profile active.',
    bannerDesc: 'Targeting a live CERBERUS backend. Connect with a valid API key before issuing hardware commands.',
    connectionSummary: 'PythonServer expects a live CERBERUS backend and Go2 bridge. Keep simulation off unless you are deliberately rehearsing without hardware.',
    authCopy: 'Enter a valid API key to connect to the live CERBERUS backend. Use simulation only for dry runs and UI rehearsal.',
    defaultApiBase: 'http://localhost:8080',
    preferSim: false,
    requireKeyPrompt: true,
    connectButton: 'Connect Go2 Backend',
  },
};

const CONTROL_LOCK = {
  status: 'pending',
  title: 'Awaiting profile initialization.',
  detail: 'Live controls have not been evaluated yet.',
  evidence: [],
  locked: false,
  verifiedLive: false,
  checkedAt: null,
};

let verifySeq = 0;
let guardInstalled = false;

function getProfileId(value) {
  return Object.prototype.hasOwnProperty.call(PROFILES, value) ? value : 'pythonserver';
}

function getRequestedProfileId() {
  const params = new URLSearchParams(window.location.search);
  return getProfileId(params.get('profile') || localStorage.getItem(PROFILE_STORE) || document.body?.dataset?.controlProfile || 'pythonserver');
}

function syncSelect(id, value) {
  const node = el(id);
  if (node) node.value = value;
}

function updateText(id, text, html = false) {
  const node = el(id);
  if (!node) return;
  if (html) node.innerHTML = text;
  else node.textContent = text;
}

function maybeReplaceApiBase(profile) {
  const urlEl = el('api-url');
  if (!urlEl) return;
  const currentValue = (urlEl.value || '').trim();
  const oldDefault = P.apiBase;
  if (!currentValue || currentValue === oldDefault || currentValue === PROFILES.localhost.defaultApiBase || currentValue === PROFILES.pythonserver.defaultApiBase) {
    urlEl.value = profile.defaultApiBase;
  }
  P.apiBase = (urlEl.value || profile.defaultApiBase).trim() || profile.defaultApiBase;
}

function reflectProfile(profileId) {
  const profile = PROFILES[profileId];
  document.body.dataset.controlProfile = profile.id;

  syncSelect('control-profile-switch', profile.id);
  syncSelect('control-profile-select', profile.id);

  updateText('control-profile-label', profile.label);
  updateText('control-profile-desc', profile.description);
  updateText('control-profile-banner-title', profile.bannerTitle);
  updateText('control-profile-banner-desc', profile.bannerDesc);
  updateText('connection-profile-summary', profile.connectionSummary);
  updateText('auth-profile-copy', profile.authCopy, true);

  const badge = el('control-profile-badge');
  if (badge) {
    badge.className = `terrain-chip ${profile.badgeTone}`;
    badge.textContent = profile.shortLabel;
  }

  const connectBtn = el('control-profile-connect');
  if (connectBtn) connectBtn.textContent = profile.connectButton;

  const simChk = el('sim-chk');
  if (simChk) simChk.checked = !!profile.preferSim;

  maybeReplaceApiBase(profile);

  if (!P.connected) {
    const modeBadge = el('mode-badge');
    if (modeBadge) {
      modeBadge.textContent = profile.modeBadge;
      modeBadge.className = `mode-badge ${profile.preferSim ? '' : 'warn'}`.trim();
    }
  }
}

function persistProfile(profileId) {
  localStorage.setItem(PROFILE_STORE, profileId);
  const url = new URL(window.location.href);
  url.searchParams.set('profile', profileId);
  history.replaceState({}, '', url);
}

function setControlLockState(partial) {
  Object.assign(CONTROL_LOCK, partial, { checkedAt: partial?.checkedAt ?? CONTROL_LOCK.checkedAt ?? new Date().toISOString() });
  renderControlLockState();
}

function renderControlLockState() {
  window.__cerberusControlVerification = { ...CONTROL_LOCK };
  const badge = el('control-live-badge');
  const summary = el('control-live-summary');
  const details = el('control-live-details');
  const panel = el('control-live-panel');
  const stamp = el('control-live-checked-at');

  if (badge) {
    const cls = CONTROL_LOCK.verifiedLive ? 'ok' : CONTROL_LOCK.locked ? 'warn' : 'idle';
    badge.className = `tval ${cls}`.trim();
    badge.textContent = CONTROL_LOCK.verifiedLive ? 'LIVE VERIFIED' : CONTROL_LOCK.locked ? 'LOCKED' : 'SIM / SAFE';
  }
  if (summary) summary.textContent = CONTROL_LOCK.title;
  if (details) details.textContent = CONTROL_LOCK.detail;
  if (stamp) stamp.textContent = CONTROL_LOCK.checkedAt ? new Date(CONTROL_LOCK.checkedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '—';
  if (panel) {
    panel.innerHTML = CONTROL_LOCK.evidence?.length
      ? CONTROL_LOCK.evidence.map(item => `<div>• ${escapeHtml(item)}</div>`).join('')
      : '<div>• No verification evidence recorded yet.</div>';
  }

  const lockNodes = document.querySelectorAll('[data-live-control]');
  lockNodes.forEach((node) => {
    const exempt = node.dataset.liveControl === 'always';
    const disabled = !exempt && !!CONTROL_LOCK.locked;
    if ('disabled' in node) node.disabled = disabled;
    node.classList.toggle('control-locked', disabled);
    node.setAttribute('aria-disabled', disabled ? 'true' : 'false');
    if (disabled) node.title = CONTROL_LOCK.detail || 'Live controls locked until backend verification succeeds.';
    else if (node.dataset.origTitle) node.title = node.dataset.origTitle;
  });
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function installLiveControlGuard() {
  if (guardInstalled) return;
  guardInstalled = true;

  const autoLockSelectors = [
    '#arm-btn',
    '#tab-home .qa-btn',
    '#tab-manual .qact-btn',
    '#tab-manual .pol-opt',
    '#tab-manual .beh-btn',
    '#tab-manual input[type="range"]',
    '#tab-tricks button',
    '#tab-anim .btn',
    '#tab-anim .fmt-btn',
    '#tab-objects .btn',
    '#tab-missions .btn',
    '#tab-bt .btn',
    '#tab-funscript .btn',
    '#minover button',
  ];
  document.querySelectorAll(autoLockSelectors.join(',')).forEach((node) => {
    if (!node.dataset.liveControl) node.dataset.liveControl = 'required';
  });
  document.querySelectorAll('#estop-btn, .estop-btn, .min-estop, #control-profile-apply, #control-profile-connect, #control-live-refresh').forEach((node) => {
    node.dataset.liveControl = 'always';
  });

  document.querySelectorAll('[data-live-control]').forEach((node) => {
    if (node.title) node.dataset.origTitle = node.title;
  });

  const blocker = (event) => {
    const target = event.target?.closest?.('[data-live-control]');
    if (!target || target.dataset.liveControl === 'always' || !CONTROL_LOCK.locked) return;
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation?.();
    log('warn', CONTROL_LOCK.detail || 'Live control is locked until backend verification succeeds');
  };

  document.addEventListener('click', blocker, true);
  document.addEventListener('input', blocker, true);
  document.addEventListener('change', blocker, true);
}

function setSafeSimulationState(profile) {
  setControlLockState({
    status: 'sim',
    title: `${profile.label} is in safe simulation mode.`,
    detail: 'Live Go2-only controls are not required. Browser-local simulation remains available for rehearsal and UI testing.',
    evidence: ['Simulation profile selected.', 'No live backend verification required.'],
    locked: false,
    verifiedLive: false,
    checkedAt: new Date().toISOString(),
  });
}

function setPendingVerification(reason) {
  setControlLockState({
    status: 'pending',
    title: 'Verifying PythonServer / Go2 backend…',
    detail: reason || 'Live command surfaces stay locked until the controller confirms a reachable CERBERUS backend and likely Go2 bridge.',
    evidence: ['Waiting on /health, /ready, /state, /capabilities, and /plugins probes.'],
    locked: true,
    verifiedLive: false,
    checkedAt: new Date().toISOString(),
  });
}

function activeProfile() {
  return PROFILES[getRequestedProfileId()];
}

async function fetchProbe(path) {
  const key = loadKey();
  const headers = { 'Content-Type': 'application/json' };
  if (key) headers['X-CERBERUS-Key'] = key;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), VERIFY_TIMEOUT_MS);
  try {
    const response = await fetch(`${P.apiBase}${path}`, { method: 'GET', headers, signal: ctrl.signal });
    const text = await response.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text || null; }
    return { ok: response.ok, status: response.status, data, error: response.ok ? null : (data?.detail || data?.error || text || `HTTP ${response.status}`) };
  } catch (error) {
    return { ok: false, status: 0, data: null, error: error?.name === 'AbortError' ? 'timeout' : (error?.message || String(error)) };
  } finally {
    clearTimeout(timer);
  }
}

function countRobotSignals(stateData) {
  if (!stateData || typeof stateData !== 'object') return 0;
  const signals = [
    'battery_percent',
    'battery_voltage',
    'foot_forces',
    'motor_temps',
    'joint_states',
    'imu',
    'odom',
    'estop_active',
    'state',
  ];
  return signals.reduce((count, key) => count + (key in stateData ? 1 : 0), 0);
}

function looksLikeGo2Bridge(pluginRows) {
  const rows = Array.isArray(pluginRows) ? pluginRows : [];
  const names = rows
    .flatMap(item => [item?.name, item?.id, item?.plugin, item?.slug])
    .filter(Boolean)
    .map(value => String(value).toLowerCase());
  return names.some(name => /(go2|unitree|bridge|cerberus)/.test(name));
}

function hasMotionCapabilities(capData) {
  const raw = [];
  const push = (value) => {
    if (!value) return;
    if (Array.isArray(value)) value.forEach(push);
    else if (typeof value === 'object') Object.entries(value).forEach(([key, inner]) => {
      if (inner === true) raw.push(key);
      else push(inner);
    });
    else raw.push(String(value));
  };
  push(capData?.capabilities);
  push(capData?.actions);
  push(capData);
  return raw.some(item => /(motion\.|system\.estop|system\.arm|behavior\.)/.test(String(item)));
}

function evaluateVerification(probes) {
  const evidence = [];
  let score = 0;

  if (probes.health.ok) {
    score += 1;
    evidence.push(`/health responded (${probes.health.status}).`);
  } else if (probes.health.error) {
    evidence.push(`/health probe failed: ${probes.health.error}.`);
  }

  if (probes.ready.ok) {
    score += 1;
    evidence.push(`/ready responded (${probes.ready.status}).`);
  } else if (probes.ready.error) {
    evidence.push(`/ready probe failed: ${probes.ready.error}.`);
  }

  const stateSignals = countRobotSignals(probes.state.data);
  if (probes.state.ok && stateSignals > 0) {
    score += 2;
    evidence.push(`/state exposed ${stateSignals} robot-state signal${stateSignals === 1 ? '' : 's'}.`);
  } else if (probes.state.ok) {
    evidence.push('/state responded but did not expose clear robot-state signals.');
  } else if (probes.state.error) {
    evidence.push(`/state probe failed: ${probes.state.error}.`);
  }

  if (probes.plugins.ok && looksLikeGo2Bridge(probes.plugins.data)) {
    score += 2;
    evidence.push('/plugins looks consistent with a CERBERUS / Go2 bridge stack.');
  } else if (probes.plugins.ok) {
    evidence.push('/plugins responded but did not clearly identify a Go2 bridge.');
  } else if (probes.plugins.error) {
    evidence.push(`/plugins probe failed: ${probes.plugins.error}.`);
  }

  if (probes.capabilities.ok && hasMotionCapabilities(probes.capabilities.data)) {
    score += 1;
    evidence.push('/capabilities advertises motion / system command surfaces.');
  } else if (probes.capabilities.ok) {
    evidence.push('/capabilities responded but advertised command surface is limited.');
  } else if (probes.capabilities.error) {
    evidence.push(`/capabilities probe failed: ${probes.capabilities.error}.`);
  }

  const controllerReachable = probes.health.ok || probes.ready.ok || probes.state.ok || probes.plugins.ok || probes.capabilities.ok;
  const verifiedLive = score >= 4 && probes.state.ok && stateSignals > 0;

  if (verifiedLive) {
    return {
      status: 'verified',
      title: 'PythonServer backend verified for live Go2 operations.',
      detail: 'Live controls are unlocked because the controller responded with robot-state evidence and a compatible CERBERUS surface.',
      evidence,
      locked: false,
      verifiedLive: true,
    };
  }

  if (controllerReachable) {
    return {
      status: 'degraded',
      title: 'Controller reachable, but live Go2 verification is incomplete.',
      detail: 'Dangerous controls remain locked until the backend exposes stronger robot-state and bridge evidence.',
      evidence,
      locked: true,
      verifiedLive: false,
    };
  }

  return {
    status: 'offline',
    title: 'PythonServer backend is not reachable yet.',
    detail: 'Live controls remain locked until the CERBERUS backend answers verification probes.',
    evidence,
    locked: true,
    verifiedLive: false,
  };
}

async function verifyPythonServerLiveBackend(reason = 'Connection requested') {
  const profile = activeProfile();
  if (profile.id !== 'pythonserver') {
    setSafeSimulationState(profile);
    return CONTROL_LOCK;
  }

  if (!loadKey()) {
    setControlLockState({
      status: 'auth-required',
      title: 'API key required before live verification can run.',
      detail: 'PythonServer mode keeps live controls locked until an operator key is present and the backend can be probed.',
      evidence: ['No API key is currently loaded.'],
      locked: true,
      verifiedLive: false,
      checkedAt: new Date().toISOString(),
    });
    return CONTROL_LOCK;
  }

  const seq = ++verifySeq;
  setPendingVerification(reason);

  const [health, ready, state, capabilities, plugins] = await Promise.all([
    fetchProbe('/health'),
    fetchProbe('/ready'),
    fetchProbe('/state'),
    fetchProbe('/capabilities'),
    fetchProbe('/plugins'),
  ]);

  if (seq !== verifySeq) return CONTROL_LOCK;

  setControlLockState({ ...evaluateVerification({ health, ready, state, capabilities, plugins }), checkedAt: new Date().toISOString() });
  return CONTROL_LOCK;
}

function activateProfile(profileId, { reconnect = false, silent = false } = {}) {
  const normalized = getProfileId(profileId);
  const profile = PROFILES[normalized];
  persistProfile(normalized);
  reflectProfile(normalized);

  if (profile.preferSim) {
    enterSimMode();
    setSafeSimulationState(profile);
    if (!silent) log('info', `Control profile set to ${profile.label} — browser simulation preferred`);
    return normalized;
  }

  setPendingVerification('PythonServer profile selected. Waiting for live backend verification.');

  if (reconnect) {
    const key = loadKey();
    if (key) {
      reconnectWS();
      verifyPythonServerLiveBackend('Reconnect requested after switching to PythonServer mode.');
      if (!silent) log('info', `Control profile set to ${profile.label} — reconnecting live backend`);
    } else {
      showAuthModal();
      if (!silent) log('warn', `Control profile set to ${profile.label} — API key required before connecting`);
    }
  } else if (!silent) {
    log('info', `Control profile set to ${profile.label}`);
  }
  return normalized;
}

function connectUsingCurrentProfile() {
  const profileId = getProfileId(el('control-profile-select')?.value || el('control-profile-switch')?.value || getRequestedProfileId());
  const profile = PROFILES[profileId];
  reflectProfile(profileId);

  if (profile.preferSim) {
    enterSimMode();
    setSafeSimulationState(profile);
    log('info', 'LocalHost profile staying in simulation mode');
    return;
  }

  const key = loadKey();
  if (!key) {
    showAuthModal();
    log('warn', 'PythonServer profile selected — API key required');
    setControlLockState({
      status: 'auth-required',
      title: 'PythonServer mode is waiting for an API key.',
      detail: 'Live command surfaces stay locked until an operator key is supplied and backend verification succeeds.',
      evidence: ['Connect was requested without an API key.'],
      locked: true,
      verifiedLive: false,
      checkedAt: new Date().toISOString(),
    });
    return;
  }
  setPendingVerification('Connecting to PythonServer backend…');
  connectWS();
  verifyPythonServerLiveBackend(`Operator requested connection to ${P.apiBase}.`);
  log('info', `Connecting using ${profile.label}`);
}

export function getControlProfile() {
  return PROFILES[getRequestedProfileId()];
}

export function getControlVerification() {
  return { ...CONTROL_LOCK };
}

export function canIssueLiveCommands() {
  return !CONTROL_LOCK.locked;
}

export function requestLiveBackendVerification(reason) {
  return verifyPythonServerLiveBackend(reason);
}

export function initControlProfile() {
  const initialId = getRequestedProfileId();
  reflectProfile(initialId);
  persistProfile(initialId);
  installLiveControlGuard();

  if (PROFILES[initialId].preferSim) setSafeSimulationState(PROFILES[initialId]);
  else setPendingVerification('PythonServer profile loaded. Waiting for backend verification.');

  el('control-profile-switch')?.addEventListener('change', (event) => {
    const nextId = getProfileId(event.target.value);
    syncSelect('control-profile-select', nextId);
    activateProfile(nextId, { reconnect: nextId === 'localhost', silent: false });
  });

  el('control-profile-select')?.addEventListener('change', (event) => {
    const nextId = getProfileId(event.target.value);
    syncSelect('control-profile-switch', nextId);
    reflectProfile(nextId);
    persistProfile(nextId);
    if (PROFILES[nextId].preferSim) setSafeSimulationState(PROFILES[nextId]);
    else setPendingVerification('PythonServer profile selected. Apply or connect to verify backend.');
  });

  el('control-profile-apply')?.addEventListener('click', () => {
    const nextId = getProfileId(el('control-profile-select')?.value || initialId);
    syncSelect('control-profile-switch', nextId);
    activateProfile(nextId, { reconnect: nextId === 'pythonserver', silent: false });
  });

  el('control-profile-connect')?.addEventListener('click', connectUsingCurrentProfile);
  el('control-live-refresh')?.addEventListener('click', () => verifyPythonServerLiveBackend('Manual live-verification refresh requested.'));

  window.addEventListener('cerberus:ws-open', () => {
    if (activeProfile().id === 'pythonserver') verifyPythonServerLiveBackend('WebSocket opened; confirming live backend surfaces.');
  });
  window.addEventListener('cerberus:ws-close', () => {
    if (activeProfile().id === 'pythonserver') {
      setControlLockState({
        status: 'disconnected',
        title: 'PythonServer connection closed.',
        detail: 'Live controls have been re-locked until the backend reconnects and verification succeeds again.',
        evidence: ['WebSocket connection closed.'],
        locked: true,
        verifiedLive: false,
        checkedAt: new Date().toISOString(),
      });
    }
  });
  window.addEventListener('cerberus:sim-mode', () => setSafeSimulationState(activeProfile()));

  return PROFILES[initialId];
}
