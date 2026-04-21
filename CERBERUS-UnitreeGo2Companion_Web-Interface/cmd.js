/**
 * cmd.js — apiCmd: translates UI action strings to CERBERUS controller calls.
 *
 * Primary path:
 *   1. Try the newer controller /execute contract with a standardized envelope.
 *   2. Fall back to legacy direct REST endpoints when /execute is unavailable or
 *      rejects the standardized action.
 *
 * This keeps the existing UI working while making the controller ready for the
 * Sweetie-Bot style orchestration contract.
 */

import { P, EP, BEHAVIOR_TO_SPORT, log, loadKey } from './config.js';
import { apiPost }                                 from './auth.js';
import { canIssueLiveCommands, getControlProfile } from './control-profile.js';

const EXECUTE_TIMEOUT_MS = 1800;
const EXECUTE_PROBE_TTL_MS = 10000;

let executeSurface = {
  checkedAt: 0,
  available: null,
};

export async function apiCmd(action, params = {}) {
  log('info', '→ ' + action);

  if (_requiresVerifiedLiveBackend(action) && !canIssueLiveCommands()) {
    const profile = getControlProfile();
    const reason = profile?.id === 'pythonserver'
      ? 'Live backend not verified yet — command blocked for safety'
      : 'Command blocked until profile is switched out of safe simulation mode';
    log('warn', `${action} blocked: ${reason}`);
    return { ok: false, reason };
  }

  if (P.simMode || !P.connected) {
    window._simCmd?.(action, params);
    return { ok: true, simulated: true, action, params };
  }

  try {
    const result = await _dispatch(action, params);
    if (result?.ok !== false) log('ok', '✓ ' + action);
    else log('err', `✗ ${action}: ${result?.detail || result?.reason || 'failed'}`);
    return result ?? { ok: true };
  } catch (e) {
    log('err', `${action} failed: ${e.message}`);
    return { ok: false, reason: e.message };
  }
}

async function _dispatch(action, params) {
  const executeResult = await _tryExecute(action, params);
  if (executeResult?.ok) return executeResult;

  switch (action) {
    case 'STAND':        return apiPost(EP.standUp);
    case 'SIT':          return apiPost(EP.sportMode, { mode: 'sit' });
    case 'STOP':         return apiPost(EP.stop);
    case 'ESTOP':        return apiPost(EP.estop);
    case 'CLEAR_ESTOP':  return apiPost(EP.clearEstop);
    case 'ARM':          return { ok: true, detail: 'No arm/disarm concept in CERBERUS' };
    case 'DISARM':       return { ok: true, detail: 'No arm/disarm concept in CERBERUS' };
    case 'FOLLOW':       return apiPost(EP.goalPost, { name: 'explore', priority: 0.5 });
    case 'NAVIGATE':     return apiPost(EP.goalPost, { name: 'explore', priority: 0.5 });
    case 'WALK':         return apiPost(EP.move, { vx: params.vx ?? 0.3, vy: params.vy ?? 0, vyaw: params.vyaw ?? 0 });
    case 'SET_POLICY':   return _setPolicy(params.policy);
    case 'RUN_BEHAVIOR': return _runBehavior(params);
    case 'SPORT_MODE':   return apiPost(EP.sportMode, { mode: params.mode });
    case 'BODY_CTRL':    return _bodyCtrl(params);
    case 'SET_TARGET':   return { ok: true, detail: 'Target is tracked client-side only' };
    default:
      log('warn', 'Unknown action: ' + action);
      return {
        ok: false,
        reason: executeResult?.reason || ('Unknown action: ' + action),
        detail: executeResult?.detail || null,
      };
  }
}

async function _tryExecute(action, params) {
  const envelope = _buildExecuteEnvelope(action, params);
  if (!envelope) return null;

  const available = await _executeAvailable();
  if (!available) return { ok: false, reason: 'Controller /execute unavailable' };

  try {
    const response = await _fetchWithTimeout(`${P.apiBase}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(envelope),
    }, EXECUTE_TIMEOUT_MS);

    const data = await _readJson(response);
    if (!response.ok) {
      const detail = data?.detail || data?.error || `HTTP ${response.status}`;
      if ([400, 404, 405, 422, 501].includes(response.status)) {
        return { ok: false, reason: 'Controller /execute rejected command', detail };
      }
      throw new Error(detail);
    }

    executeSurface.available = true;
    executeSurface.checkedAt = Date.now();
    return _normalizeExecuteResponse(action, envelope, data);
  } catch (error) {
    const message = error?.message || String(error);
    if (_isExecuteSurfaceError(message)) {
      executeSurface.available = false;
      executeSurface.checkedAt = Date.now();
      return { ok: false, reason: 'Controller /execute unavailable', detail: message };
    }
    throw error;
  }
}

async function _executeAvailable() {
  const now = Date.now();
  if (executeSurface.available !== null && (now - executeSurface.checkedAt) < EXECUTE_PROBE_TTL_MS) {
    return executeSurface.available;
  }

  try {
    const response = await _fetchWithTimeout(`${P.apiBase}/execute`, {
      method: 'OPTIONS',
      headers: { 'Content-Type': 'application/json' },
    }, 1200);
    executeSurface.available = response.ok;
  } catch {
    executeSurface.available = false;
  }

  executeSurface.checkedAt = now;
  return executeSurface.available;
}

function _buildExecuteEnvelope(action, params) {
  const mapped = _mapAction(action, params);
  if (!mapped) return null;

  const requestId = `ui-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  return {
    id: requestId,
    request_id: requestId,
    timestamp: new Date().toISOString(),
    source: 'web-interface',
    action: mapped.action,
    params: mapped.params,
    input: mapped.params,
    priority: mapped.priority || 'normal',
    timeout_ms: mapped.timeout_ms || EXECUTE_TIMEOUT_MS,
    context: {
      ui_action: action,
      sim_mode: !!P.simMode,
      estop: !!P.estop,
      connected: !!P.connected,
      locale: P.locale,
    },
    state: {
      controller: {
        connected: !!P.connected,
        estop: !!P.estop,
        sim_mode: !!P.simMode,
      },
      telemetry: P.telemetry || {},
      terrain: P.terrain || null,
      safety: P.safety || {},
    },
  };
}

function _mapAction(action, params) {
  switch (action) {
    case 'STAND':
      return { action: 'motion.stand', params: {} };
    case 'SIT':
      return { action: 'motion.sit', params: {} };
    case 'STOP':
      return { action: 'motion.stop', params: { emergency: false }, priority: 'high' };
    case 'ESTOP':
      return { action: 'system.estop', params: { emergency: true }, priority: 'critical' };
    case 'CLEAR_ESTOP':
      return { action: 'system.clear_estop', params: {}, priority: 'high' };
    case 'ARM':
      return { action: 'system.arm', params: {} };
    case 'DISARM':
      return { action: 'system.disarm', params: {} };
    case 'FOLLOW':
      return {
        action: 'behavior.follow',
        params: {
          target: params.target || 'operator',
          standoff_m: params.standoff_m ?? 0.8,
        },
      };
    case 'NAVIGATE':
      return {
        action: 'behavior.navigate',
        params: {
          goal: params.goal || params.target || 'explore',
          x: params.x,
          y: params.y,
          yaw: params.yaw,
        },
      };
    case 'WALK':
      return {
        action: 'motion.move',
        params: {
          vx: params.vx ?? 0.3,
          vy: params.vy ?? 0,
          vyaw: params.vyaw ?? 0,
        },
      };
    case 'SET_POLICY':
      return {
        action: 'motion.set_policy',
        params: { policy: params.policy || P.policy || 'SMOOTH' },
      };
    case 'RUN_BEHAVIOR':
      return {
        action: 'behavior.run',
        params: {
          behavior_id: params.behavior_id,
          behavior: params.behavior_id,
        },
      };
    case 'SPORT_MODE':
      return {
        action: 'motion.sport_mode',
        params: { mode: params.mode },
      };
    case 'BODY_CTRL':
      return {
        action: 'motion.body_control',
        params: _normalizeBodyParams(params),
      };
    case 'SET_TARGET':
      return {
        action: 'perception.set_target',
        params: { target: params.target ?? null },
      };
    default:
      return {
        action,
        params: params || {},
      };
  }
}

function _normalizeBodyParams(params = {}) {
  const next = { ...params };
  if ('roll' in next) next.roll_rad = (next.roll || 0) * Math.PI / 180;
  if ('yaw' in next) next.yaw_rad = (next.yaw || 0) * Math.PI / 180;
  if (!('pitch_rad' in next)) next.pitch_rad = 0;
  return next;
}

function _normalizeExecuteResponse(uiAction, envelope, data) {
  const status = data?.status || data?.state || 'accepted';
  const ok = data?.ok !== false && !['failed', 'rejected', 'error'].includes(String(status).toLowerCase());
  return {
    ok,
    via: '/execute',
    action: uiAction,
    command_action: envelope.action,
    id: data?.id || data?.request_id || envelope.id,
    status,
    detail: data?.detail || data?.message || null,
    raw: data,
  };
}

function _runBehavior({ behavior_id: bid }) {
  const mode = BEHAVIOR_TO_SPORT[bid];
  return mode
    ? apiPost(EP.sportMode, { mode })
    : apiPost(EP.goalPost, { name: bid, priority: 0.7 });
}

function _setPolicy(policy) {
  const map = { SMOOTH: 1, STABLE: 2, AGILE: 3, ADAPTIVE: 4 };
  return apiPost(EP.gait, { gait_id: map[policy] ?? 1 });
}

function _bodyCtrl(params) {
  if ('height' in params) return apiPost(EP.bodyHeight, { height: params.height });
  if ('roll' in params || 'yaw' in params)
    return apiPost(EP.euler, {
      roll:  (params.roll  || 0) * Math.PI / 180,
      pitch: 0,
      yaw:   (params.yaw   || 0) * Math.PI / 180,
    });
  if ('speed' in params) return apiPost(EP.move, { vx: params.speed, vy: 0, vyaw: 0 });
  return { ok: true };
}

function _isExecuteSurfaceError(message) {
  return /Failed to fetch|NetworkError|Network error|404|405|Cannot POST|Cannot OPTIONS|Not Found/i.test(String(message || ''));
}

async function _readJson(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

async function _fetchWithTimeout(url, options, timeoutMs) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const headers = { ...(options?.headers || {}) };
  const key = loadKey();
  if (key) headers['X-CERBERUS-Key'] = key;

  try {
    return await fetch(url, { ...options, headers, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

function _requiresVerifiedLiveBackend(action) {
  return !['ESTOP', 'CLEAR_ESTOP'].includes(String(action || '').toUpperCase());
}
