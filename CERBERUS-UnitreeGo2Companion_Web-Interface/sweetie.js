import { el, log, P } from './config.js';
import { apiFetch } from './api.js';

const STORAGE_KEY = 'sweetie_controller_endpoints_v4';

const DEFAULTS = {
  eventBus: 'http://localhost:7101',
  actionRegistry: 'http://localhost:7102',
  gaitLibrary: 'http://localhost:7103',
  socialBonding: 'http://localhost:7104',
  crusaderLink: 'http://localhost:7105',
  autonomySupervisor: 'http://localhost:7106',
  perceptionAdapter: 'http://localhost:7201',
  motionAdapter: 'http://localhost:7202',
  batteryAdapter: 'http://localhost:7203',
  audioAdapter: 'http://localhost:7204',
  peerAdapter: 'http://localhost:7205',
};

const LEGACY_KEY_ALIASES = {
  runtime: 'autonomySupervisor',
  worldModel: 'perceptionAdapter',
  memory: 'socialBonding',
};

const DEFAULT_SESSION = {
  session_id: 'controller-session',
  conversation_id: null,
  actor_id: 'sweetie-bot',
  environment_id: 'cerberus-controller',
};

const REQUEST_TIMEOUT_MS = 2500;
const HISTORY_LIMIT = 50;
const ACTIVE_RENDER_LIMIT = 4;
const HISTORY_RENDER_LIMIT = 8;

const QUICK_ACTIONS = {
  follow_best_friend: {
    endpoint: 'autonomySupervisor',
    action: 'autonomy.execute',
    input: {
      mode: 'follow_best_friend',
      target_id: 'operator-001',
      standoff_m: 0.8,
      reason: 'operator-request',
    },
    fallback: {
      type: 'autonomy.execute',
      payload: {
        mode: 'follow_best_friend',
        target_id: 'operator-001',
        standoff_m: 0.8,
        reason: 'operator-request',
      },
    },
    capabilityHints: ['autonomy.execute', 'runtime.execute', 'runtime.chain_execute', 'action.dispatch'],
    confirm: 'Command robot to follow the best-friend/operator target?',
  },
  force_dock: {
    endpoint: 'autonomySupervisor',
    action: 'autonomy.execute',
    input: {
      mode: 'dock',
      dock_id: 'charging-dock-1',
      reason: 'operator-request',
      priority: 'high',
    },
    fallback: {
      type: 'autonomy.execute',
      payload: {
        mode: 'dock',
        dock_id: 'charging-dock-1',
        reason: 'operator-request',
        priority: 'high',
      },
    },
    capabilityHints: ['autonomy.execute', 'runtime.execute', 'action.dispatch'],
    confirm: 'Force Sweetie into dock mode now?',
  },
  safe_stop: {
    endpoint: 'motionAdapter',
    action: 'motion.stop',
    input: { emergency: true, source: 'operator' },
    fallback: { type: 'motion.stop', payload: { emergency: true, source: 'operator' } },
    capabilityHints: ['motion.stop', 'robot.stop', 'cerberus-bridge.execute'],
    confirm: 'Send an immediate safe-stop to the motion adapter?',
  },
  clear_autonomy_override: {
    endpoint: 'autonomySupervisor',
    action: 'autonomy.override.clear',
    input: { source: 'operator', resume_policy: 'supervisor_default' },
    fallback: { type: 'autonomy.override.clear', payload: { source: 'operator', resume_policy: 'supervisor_default' } },
    capabilityHints: ['autonomy.override.clear', 'autonomy.execute', 'runtime.execute'],
  },
  peer_status_ping: {
    endpoint: 'peerAdapter',
    action: 'peer.status_ping',
    input: { source: 'operator-console', preferred_transport_order: ['bluetooth', 'wifi', 'voice'] },
    fallback: { type: 'peer.status_ping', payload: { source: 'operator-console', preferred_transport_order: ['bluetooth', 'wifi', 'voice'] } },
    capabilityHints: ['peer.status_ping', 'peer.execute', 'runtime.execute'],
  },
  follow_operator: {
    aliasFor: 'follow_best_friend',
  },
  patrol_basic: {
    endpoint: 'autonomySupervisor',
    action: 'autonomy.execute',
    input: {
      mode: 'patrol',
      waypoints: [
        { x: 0, y: 0 },
        { x: 1.5, y: 0 },
        { x: 1.5, y: 1.5 },
      ],
      loop: true,
    },
    fallback: {
      type: 'autonomy.execute',
      payload: {
        mode: 'patrol',
        waypoints: [
          { x: 0, y: 0 },
          { x: 1.5, y: 0 },
          { x: 1.5, y: 1.5 },
        ],
        loop: true,
      },
    },
    capabilityHints: ['autonomy.execute', 'runtime.execute', 'runtime.chain_execute', 'action.dispatch'],
  },
};

function loadLegacyCfgSnapshot() {
  for (const key of [STORAGE_KEY, 'sweetie_controller_endpoints_v3']) {
    try {
      const parsed = JSON.parse(localStorage.getItem(key) || '{}');
      if (parsed && typeof parsed === 'object' && Object.keys(parsed).length) return parsed;
    } catch {}
  }
  return {};
}

function migrateCfg(raw) {
  const next = { ...DEFAULTS };
  Object.entries(raw || {}).forEach(([key, value]) => {
    const targetKey = LEGACY_KEY_ALIASES[key] || key;
    if (targetKey in next && value) next[targetKey] = value;
  });
  return next;
}

function loadCfg() {
  try {
    return migrateCfg(loadLegacyCfgSnapshot());
  } catch {
    return { ...DEFAULTS };
  }
}

function saveCfg(cfg) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg));
  try { localStorage.removeItem('sweetie_controller_endpoints_v3'); } catch {}
}

function escHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function compactJson(value, max = 120) {
  try {
    const raw = typeof value === 'string' ? value : JSON.stringify(value);
    return raw.length > max ? `${raw.slice(0, Math.max(0, max - 1))}…` : raw;
  } catch {
    return String(value ?? '');
  }
}

function titleizeKey(key) {
  return key
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .replace(/^./, c => c.toUpperCase());
}

function endpointGroup(key) {
  if (/(Adapter)$/i.test(key)) return 'Adapter';
  if (/eventBus|actionRegistry|gaitLibrary/i.test(key)) return 'Core';
  if (/runtime|autonomySupervisor/i.test(key)) return 'Orchestrator';
  return 'Plugin';
}

function formatStateValue(value, max = 32) {
  if (value == null || value === '') return '—';
  return compactJson(value, max);
}

function setText(id, value, cls = null) {
  const node = el(id);
  if (!node) return;
  node.textContent = value;
  if (cls != null) node.className = `tval ${cls}`.trim();
}

function setQuickActionState(label, state = 'idle') {
  const node = el('sweetie-quick-action-status');
  if (!node) return;
  node.textContent = label;
  node.className = `tval ${state}`.trim();
}

function row(name, key, value) {
  return `<div class="srow"><div><div class="slabel">${escHtml(name)}</div><div class="sdesc">${escHtml(key)}</div></div><input id="sweetie-${escHtml(key)}" type="text" value="${escHtml(value)}" style="width:240px"></div>`;
}

function nowIso() {
  return new Date().toISOString();
}

function nowMs() {
  return Date.now();
}

function formatDurationMs(value) {
  const ms = Number(value);
  if (!Number.isFinite(ms) || ms < 0) return '—';
  if (ms < 1000) return `${Math.round(ms)} ms`;
  const sec = ms / 1000;
  if (sec < 60) return `${sec.toFixed(sec >= 10 ? 0 : 1)} s`;
  const min = Math.floor(sec / 60);
  const rem = Math.round(sec % 60);
  return `${min}m ${rem}s`;
}

function formatIsoTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function newRequestId(prefix = 'sweetie') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function flattenCapabilities(...sources) {
  const out = new Set();
  for (const source of sources) {
    if (!source) continue;
    if (Array.isArray(source)) {
      source.forEach(item => {
        if (typeof item === 'string' && item.trim()) out.add(item.trim());
      });
      continue;
    }
    if (typeof source === 'object') {
      Object.entries(source).forEach(([key, value]) => {
        if (typeof value === 'boolean' && value) out.add(key);
        if (Array.isArray(value)) value.forEach(item => typeof item === 'string' && out.add(item.trim()));
      });
    }
  }
  return Array.from(out).sort();
}

function toArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeBaseUrl(url) {
  return String(url || '').trim().replace(/\/$/, '');
}

function withTimeout(promiseFactory, timeoutMs = REQUEST_TIMEOUT_MS) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  return Promise.resolve()
    .then(() => promiseFactory(ctrl.signal))
    .finally(() => clearTimeout(timer));
}

async function fetchJson(url, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  return withTimeout(async signal => {
    const response = await fetch(url, { ...options, signal });
    const text = await response.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch {}
    if (!response.ok) {
      const detail = data?.detail || data?.error || text || `HTTP ${response.status}`;
      throw new Error(detail);
    }
    return data;
  }, timeoutMs);
}

async function safeJson(url, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  try {
    const data = await fetchJson(url, options, timeoutMs);
    return { ok: true, data, error: null };
  } catch (error) {
    return { ok: false, data: null, error: error?.message || String(error) };
  }
}

function buildExecuteEnvelope({ plugin, action, input, state, mode = 'interactive', priority = 'normal', timeoutMs = 1500, safeMode = true }) {
  const requestId = newRequestId('sweetie');
  return {
    request_id: requestId,
    timestamp: nowIso(),
    source: 'controller',
    plugin,
    action,
    session: { ...DEFAULT_SESSION },
    context: {
      trace_id: requestId,
      user_id: 'operator_001',
      priority,
      mode,
      controller_connected: !!P.connected,
    },
    state: state || {
      controller: {
        connected: !!P.connected,
        estop: !!P.estop,
        sim_mode: !!P.simMode,
        api_base: P.apiBase,
      },
      telemetry: P.telemetry || {},
      terrain: P.terrain || null,
      safety: P.safety || {},
    },
    input: input || {},
    policy: {
      dry_run: false,
      timeout_ms: timeoutMs,
      safe_mode: safeMode,
    },
  };
}

function buildLegacyPayload(spec) {
  return spec?.fallback || { type: spec?.action, payload: spec?.input || {} };
}

function summarizeControllerState(data) {
  if (!data || typeof data !== 'object') return {};
  return {
    battery: data?.battery_level ?? data?.battery_pct ?? data?.telemetry?.battery_pct ?? null,
    motion: data?.motion_state ?? data?.state ?? data?.mode ?? null,
    dock: data?.docking_state ?? data?.charging_state ?? data?.dock ?? null,
    pose: data?.pose ?? data?.odometry ?? data?.position ?? null,
    safety: data?.safety_flags ?? data?.safety ?? null,
  };
}

function summarizePluginFamilies(probes) {
  const byName = Object.fromEntries((probes || []).map(probe => [probe.name, probe]));
  const social = byName.socialBonding?.status || byName.socialBonding?.health || {};
  const battery = byName.batteryAdapter?.status || byName.batteryAdapter?.health || {};
  const peer = byName.peerAdapter?.status || byName.peerAdapter?.health || {};
  const autonomy = byName.autonomySupervisor?.status || byName.autonomySupervisor?.health || {};
  const perception = byName.perceptionAdapter?.status || byName.perceptionAdapter?.health || {};
  const motion = byName.motionAdapter?.status || byName.motionAdapter?.health || {};
  const audio = byName.audioAdapter?.status || byName.audioAdapter?.health || {};

  return {
    autonomy: {
      mode: autonomy?.mode ?? autonomy?.state ?? autonomy?.autonomy_mode ?? null,
      goal: autonomy?.goal ?? autonomy?.current_goal ?? autonomy?.mission ?? null,
      override: autonomy?.override ?? autonomy?.manual_override ?? null,
    },
    social: {
      bestFriend: social?.best_friend ?? social?.best_friend_id ?? social?.target_id ?? null,
      focus: social?.focus_target ?? social?.focus ?? null,
      bond: social?.bond_state ?? social?.relationship_tier ?? null,
    },
    battery: {
      level: battery?.battery_pct ?? battery?.battery_level ?? battery?.percent ?? null,
      dock: battery?.dock_state ?? battery?.docking_state ?? battery?.charging_state ?? null,
      charging: battery?.charging ?? battery?.is_charging ?? null,
    },
    peer: {
      state: peer?.peer_state ?? peer?.state ?? null,
      transport: peer?.transport ?? peer?.preferred_transport ?? null,
      peers: peer?.peer_count ?? peer?.connected_peers ?? null,
    },
    adapters: {
      perception: byName.perceptionAdapter?.statusText || 'missing',
      motion: byName.motionAdapter?.statusText || 'missing',
      battery: byName.batteryAdapter?.statusText || 'missing',
      audio: byName.audioAdapter?.statusText || 'missing',
      peer: byName.peerAdapter?.statusText || 'missing',
      perceptionSource: perception?.source ?? perception?.last_event ?? null,
      motionState: motion?.state ?? motion?.mode ?? null,
      audioState: audio?.state ?? audio?.mode ?? null,
    },
  };
}

class SweetieControllerBridge {
  constructor() {
    this.cfg = loadCfg();
    this.state = {
      controller: null,
      plugins: {},
      lastUpdated: null,
    };
    this.capabilities = {
      controller: {},
      plugins: {},
      merged: {},
    };
    this.commandHistory = [];
    this.activeCommands = new Map();
    this.lastRefresh = null;
    this.lastSummary = null;
  }

  reloadCfg() {
    this.cfg = loadCfg();
    return this.cfg;
  }

  updateCfgFromDom() {
    const currentCfg = this.reloadCfg();
    const next = Object.fromEntries(
      Object.keys(currentCfg).map(key => [key, el(`sweetie-${key}`)?.value.trim() || currentCfg[key]])
    );
    saveCfg(next);
    this.cfg = next;
    return next;
  }

  addCommandHistory(entry) {
    const enriched = { ts: nowIso(), ...entry };
    if (enriched.started_at && !enriched.duration_ms) {
      const finishedAt = enriched.finished_at ? new Date(enriched.finished_at).getTime() : nowMs();
      const startedAt = new Date(enriched.started_at).getTime();
      if (Number.isFinite(finishedAt) && Number.isFinite(startedAt) && finishedAt >= startedAt) {
        enriched.duration_ms = finishedAt - startedAt;
      }
    }
    this.commandHistory.unshift(enriched);
    if (this.commandHistory.length > HISTORY_LIMIT) this.commandHistory.length = HISTORY_LIMIT;
  }

  setActiveCommand(commandId, info) {
    const current = this.activeCommands.get(commandId) || {};
    const startedAt = current.started_at || info.started_at || nowIso();
    const attempts = Number.isFinite(current.attempts) ? current.attempts : Number.isFinite(info.attempts) ? info.attempts : 0;
    this.activeCommands.set(commandId, {
      ...current,
      ...info,
      started_at: startedAt,
      updated_at: nowIso(),
      attempts,
    });
  }

  markCommandAttempt(commandId, detail = {}) {
    const current = this.activeCommands.get(commandId) || { id: commandId, started_at: nowIso() };
    const attempts = Number.isFinite(current.attempts) ? current.attempts + 1 : 1;
    this.activeCommands.set(commandId, {
      ...current,
      ...detail,
      status: detail.status || 'running',
      attempts,
      started_at: current.started_at || nowIso(),
      updated_at: nowIso(),
      last_attempt_at: nowIso(),
    });
  }

  completeActiveCommand(commandId, status, result = null, error = null) {
    const current = this.activeCommands.get(commandId) || {};
    this.activeCommands.delete(commandId);
    this.addCommandHistory({
      id: commandId,
      action: current.action || result?.action || null,
      endpoint: current.endpoint || null,
      status,
      result,
      error,
      attempts: current.attempts || 0,
      started_at: current.started_at || null,
      finished_at: nowIso(),
      params: current.params || null,
      plugin: current.plugin || null,
    });
  }

  mergeCapabilities() {
    const merged = {};
    Object.entries(this.capabilities.plugins).forEach(([plugin, caps]) => {
      toArray(caps).forEach(cap => {
        if (!merged[cap]) merged[cap] = [];
        merged[cap].push(plugin);
      });
    });
    Object.entries(this.capabilities.controller).forEach(([surface, caps]) => {
      toArray(caps).forEach(cap => {
        if (!merged[cap]) merged[cap] = [];
        if (!merged[cap].includes(`controller:${surface}`)) merged[cap].push(`controller:${surface}`);
      });
    });
    this.capabilities.merged = merged;
    return merged;
  }

  async probePlugin(name, url) {
    const base = normalizeBaseUrl(url);
    if (!base) {
      const empty = {
        name,
        url,
        online: false,
        compatible: false,
        statusText: 'missing',
        detail: 'No endpoint configured',
        capabilityList: [],
        manifest: null,
        health: null,
        status: null,
        checks: { health: false, manifest: false, status: false, execute: false },
        endpoints: { execute: '/execute', health: '/health', manifest: '/manifest', status: '/status' },
        score: 0,
      };
      this.capabilities.plugins[name] = [];
      this.state.plugins[name] = null;
      return empty;
    }

    const [healthRes, manifestRes, statusRes] = await Promise.all([
      safeJson(`${base}/health`),
      safeJson(`${base}/manifest`),
      safeJson(`${base}/status`),
    ]);

    const manifest = manifestRes.data;
    const health = healthRes.data;
    const status = statusRes.data;
    const capabilityList = flattenCapabilities(
      manifest?.capabilities,
      manifest?.actions,
      manifest?.contracts,
      status?.capabilities,
      status?.actions
    );

    const checks = {
      health: healthRes.ok,
      manifest: manifestRes.ok,
      status: statusRes.ok,
      execute: !!(manifest?.entrypoints?.execute || manifestRes.ok || statusRes.ok || healthRes.ok),
    };

    const endpoints = {
      execute: manifest?.entrypoints?.execute || '/execute',
      health: manifest?.entrypoints?.health || manifest?.healthcheck || '/health',
      manifest: '/manifest',
      status: manifest?.entrypoints?.status || '/status',
    };

    const online = checks.health || checks.manifest || checks.status;
    const compatible = checks.execute && online;
    const score = Object.values(checks).filter(Boolean).length;
    const version = manifest?.version || status?.version || health?.version || null;
    const mode = status?.mode || status?.state || null;
    const reqTotal = status?.requests_total ?? status?.request_count ?? null;
    const detailParts = [
      version ? `v${version}` : null,
      mode ? `mode=${mode}` : null,
      reqTotal != null ? `req=${reqTotal}` : null,
      !version && !mode && health?.plugin ? String(health.plugin) : null,
    ].filter(Boolean);

    const probe = {
      name,
      url: base,
      online,
      compatible,
      statusText: !online ? 'offline' : compatible ? 'compatible' : 'partial',
      detail: detailParts.join(' · ') || (compatible ? 'Compatible' : 'Limited response'),
      capabilityList,
      manifest,
      health,
      status,
      checks,
      endpoints,
      score,
      errors: [healthRes, manifestRes, statusRes].filter(item => !item.ok).map(item => item.error).filter(Boolean),
    };

    this.capabilities.plugins[name] = capabilityList;
    this.state.plugins[name] = status || health || manifest || null;
    return probe;
  }

  async probeController() {
    const localChecks = [
      { key: 'state', path: '/state', caps: ['controller.state', 'robot.state'] },
      { key: 'execute', path: '/execute', method: 'OPTIONS', caps: ['controller.execute', 'robot.execute'] },
      { key: 'capabilities', path: '/capabilities', caps: ['controller.capabilities'] },
      { key: 'session', path: '/session', caps: ['controller.session'] },
      { key: 'behavior', path: '/behavior', caps: ['controller.behavior'] },
      { key: 'plugins', path: '/plugins', caps: ['controller.plugins'] },
      { key: 'terrain', path: '/terrain', caps: ['controller.terrain'] },
    ];

    const summary = {
      ok: false,
      score: 0,
      surfaces: {},
      available: [],
      missing: [],
      capabilities: [],
      goal: null,
      focus: null,
      docking: null,
      peerState: null,
      stateSummary: {},
      raw: {},
      streaming: { webSocket: !!P.ws, connected: !!P.connected },
    };

    for (const check of localChecks) {
      try {
        let data = null;
        if (check.path === '/execute') {
          data = await safeJson(`${P.apiBase.replace(/\/$/, '')}${check.path}`, { method: 'OPTIONS' }, 1500);
          if (!data.ok) throw new Error(data.error);
          summary.surfaces[check.key] = { ok: true, path: check.path, data: data.data };
        } else {
          data = await apiFetch(check.path);
          summary.surfaces[check.key] = { ok: true, path: check.path, data };
        }
        summary.available.push(check.key);
        summary.score += 1;
        summary.capabilities.push(...check.caps);
        summary.raw[check.key] = summary.surfaces[check.key].data;
      } catch (error) {
        summary.surfaces[check.key] = { ok: false, path: check.path, error: error?.message || String(error) };
        summary.missing.push(check.key);
      }
    }

    const behavior = summary.raw.behavior || {};
    const state = summary.raw.state || {};
    const capsData = summary.raw.capabilities || {};

    summary.goal = behavior?.goal || behavior?.current_goal || behavior?.mission || null;
    summary.focus = behavior?.focus_target || behavior?.focus || null;
    summary.docking = state?.docking_state || state?.charging_state || state?.dock || null;
    summary.peerState = state?.peer_state || state?.squad_state || null;
    summary.stateSummary = summarizeControllerState(state);
    summary.capabilities = flattenCapabilities(summary.capabilities, capsData?.capabilities, capsData?.actions, capsData);
    summary.ok = ['state', 'execute'].every(surface => summary.available.includes(surface));

    this.capabilities.controller = {
      core: summary.capabilities,
      state: summary.surfaces.state?.ok ? ['controller.state', 'robot.state'] : [],
      execute: summary.surfaces.execute?.ok ? ['controller.execute', 'robot.execute'] : [],
      capabilities: summary.surfaces.capabilities?.ok ? flattenCapabilities(capsData?.capabilities, capsData?.actions, capsData) : [],
    };
    this.state.controller = state;
    return summary;
  }

  async refresh() {
    this.reloadCfg();
    const pluginEntries = Object.entries(this.cfg);
    const [controller, plugins] = await Promise.all([
      this.probeController().catch(error => ({
        ok: false,
        score: 0,
        available: [],
        missing: ['state', 'execute', 'capabilities', 'session', 'behavior', 'plugins', 'terrain'],
        surfaces: {},
        streaming: { webSocket: !!P.ws, connected: !!P.connected },
        error: error?.message || String(error),
        capabilities: [],
        stateSummary: {},
      })),
      Promise.all(pluginEntries.map(([name, url]) => this.probePlugin(name, url))),
    ]);

    this.mergeCapabilities();
    this.state.lastUpdated = nowIso();
    this.lastRefresh = nowIso();
    this.lastSummary = {
      controller,
      plugins,
      compatiblePlugins: plugins.filter(plugin => plugin.compatible).length,
      onlinePlugins: plugins.filter(plugin => plugin.online).length,
      totalPlugins: plugins.length,
      mergedCapabilityCount: Object.keys(this.capabilities.merged).length,
      familySummary: summarizePluginFamilies(plugins),
    };
    return this.lastSummary;
  }

  async execute(action, params = {}, options = {}) {
    const controllerBase = normalizeBaseUrl(P.apiBase);
    const commandId = options.id || newRequestId('cmd');
    const entry = {
      id: commandId,
      action,
      endpoint: options.endpoint || 'controller',
      params,
      status: 'queued',
    };

    this.setActiveCommand(commandId, entry);

    const envelope = {
      id: commandId,
      action,
      params,
      priority: options.priority || 'normal',
      timeout_ms: options.timeout_ms || 1500,
      source: 'sweetie.js',
      plugin: options.plugin || null,
    };

    const attempts = [];

    if (controllerBase) {
      attempts.push({
        label: 'controller /execute',
        run: () => fetchJson(`${controllerBase}/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(envelope),
        }),
      });
    }

    if (options.pluginBaseUrl) {
      const base = normalizeBaseUrl(options.pluginBaseUrl);
      const standardEnvelope = buildExecuteEnvelope({
        plugin: options.plugin || options.endpoint || 'sweetie-plugin',
        action,
        input: params,
        priority: options.priority || 'normal',
        timeoutMs: options.timeout_ms || 1500,
      });
      attempts.push({
        label: 'plugin standard /execute',
        run: () => fetchJson(`${base}/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(standardEnvelope),
        }),
      });
      attempts.push({
        label: 'plugin legacy /execute',
        run: () => fetchJson(`${base}/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: action, payload: params }),
        }),
      });
    }

    let lastError = null;
    for (const attempt of attempts) {
      try {
        this.markCommandAttempt(commandId, { ...entry, status: 'running', endpoint: attempt.label, plugin: options.plugin || null });
        const result = await attempt.run();
        const status = result?.status || result?.state || 'completed';
        this.completeActiveCommand(commandId, status, result, null);
        return { ok: true, via: attempt.label, result, id: commandId };
      } catch (error) {
        lastError = error;
        this.addCommandHistory({ id: commandId, action, endpoint: attempt.label, status: 'failed_attempt', error: error?.message || String(error), attempts: (this.activeCommands.get(commandId)?.attempts || 0), started_at: this.activeCommands.get(commandId)?.started_at || null, finished_at: nowIso(), params, plugin: options.plugin || null });
      }
    }

    this.completeActiveCommand(commandId, 'failed', null, lastError?.message || 'No execution path succeeded');
    return { ok: false, id: commandId, error: lastError?.message || 'No execution path succeeded' };
  }
}

const BRIDGE = new SweetieControllerBridge();

function renderCapabilityChips(caps, emptyText = 'No capabilities advertised') {
  return caps.length
    ? caps.slice(0, 12).map(cap => `<span class="terrain-chip terrain-flat">${escHtml(cap)}</span>`).join(' ')
    : `<span style="font-size:11px;color:var(--ink3)">${escHtml(emptyText)}</span>`;
}

function renderControllerSummary(summary, globalSummary) {
  const statusClass = summary.ok ? 'ok' : summary.score >= 3 ? 'warn' : 'err';
  const statusText = summary.ok ? 'ready' : summary.score >= 3 ? 'partial' : 'limited';
  const meta = [
    summary.goal ? `goal=${compactJson(summary.goal, 36)}` : null,
    summary.focus ? `focus=${compactJson(summary.focus, 36)}` : null,
    summary.docking ? `dock=${compactJson(summary.docking, 36)}` : null,
    summary.peerState ? `peer=${compactJson(summary.peerState, 36)}` : null,
    summary.streaming.connected ? 'ws=connected' : summary.streaming.webSocket ? 'ws=attached' : 'ws=offline',
  ].filter(Boolean);

  const surfaces = Object.entries(summary.surfaces || {})
    .map(([name, info]) => `<span class="terrain-chip ${info.ok ? 'terrain-flat' : 'terrain-rough'}">${info.ok ? '✓' : '✗'} ${escHtml(name)}</span>`)
    .join(' ');

  const stateSummary = summary.stateSummary || {};
  const stateMeta = [
    stateSummary.battery != null ? `battery=${stateSummary.battery}` : null,
    stateSummary.motion ? `motion=${compactJson(stateSummary.motion, 28)}` : null,
    stateSummary.dock ? `dock=${compactJson(stateSummary.dock, 28)}` : null,
  ].filter(Boolean).join(' · ');

  return `<div class="node-row" style="display:block;padding:10px 12px;border:1px solid rgba(255,255,255,.08);border-radius:12px">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
      <span class="node-name" style="font-weight:700;flex:1">Controller bridge readiness</span>
      <span class="nst ${statusClass}">${statusText}</span>
      <span style="font-size:11px;color:var(--ink3)">${summary.score}/7 surfaces</span>
      <span style="font-size:11px;color:var(--ink3)">${globalSummary.mergedCapabilityCount} merged capabilities</span>
    </div>
    <div style="font-size:11px;color:var(--ink3);margin-top:6px">${escHtml(meta.join(' · ') || 'Checking /execute, /state, /capabilities, and legacy controller surfaces.')}</div>
    <div style="font-size:11px;color:var(--ink3);margin-top:4px">${escHtml(stateMeta || 'Waiting for controller state telemetry.')}</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">${surfaces || '<span style="font-size:11px;color:var(--ink3)">No controller surfaces detected</span>'}</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">${renderCapabilityChips(summary.capabilities || [], 'Controller capabilities not exposed')}</div>
  </div>`;
}

function renderPluginProbe(probe) {
  const statusClass = probe.compatible ? 'ok' : probe.online ? 'warn' : 'err';
  const checks = Object.entries(probe.checks)
    .map(([key, pass]) => `<span class="terrain-chip ${pass ? 'terrain-flat' : 'terrain-rough'}">${pass ? '✓' : '✗'} ${escHtml(key)}</span>`)
    .join(' ');
  const endpointMeta = [
    `exec=${probe.endpoints.execute}`,
    `health=${probe.endpoints.health}`,
    probe.endpoints.status ? `status=${probe.endpoints.status}` : null,
  ].filter(Boolean).join(' · ');

  return `<div class="node-row" style="display:block;padding:10px 12px;border:1px solid rgba(255,255,255,.08);border-radius:12px">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
      <span class="node-name" style="font-weight:700;flex:1">${escHtml(titleizeKey(probe.name))}</span>
      <span class="terrain-chip">${escHtml(endpointGroup(probe.name))}</span>
      <span class="nst ${statusClass}">${escHtml(probe.statusText)}</span>
      <span style="font-size:11px;color:var(--ink3)">${probe.score}/4</span>
    </div>
    <div style="font-size:11px;color:var(--ink3);margin-top:4px">${escHtml(probe.url)}</div>
    <div style="font-size:11px;color:var(--ink3);margin-top:4px">${escHtml(probe.detail)}</div>
    <div style="font-size:11px;color:var(--ink3);margin-top:4px">${escHtml(endpointMeta)}</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">${checks}</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">${renderCapabilityChips(probe.capabilityList)}</div>
    ${probe.errors?.length ? `<div style="font-size:11px;color:var(--danger,#ff7b7b);margin-top:8px">${escHtml(probe.errors[0])}</div>` : ''}
  </div>`;
}

function commandTone(status) {
  return /fail|err/i.test(status || '') ? 'err' : /queue|run|pending|signal|attempt/i.test(status || '') ? 'warn' : 'ok';
}

function renderCommandRow(entry, active = false) {
  const state = entry.status || (active ? 'running' : 'completed');
  const tone = commandTone(state);
  const detail = entry.error || compactJson(entry.result || entry.params || entry.detail || '', 92);
  const timing = [
    entry.started_at ? `start ${formatIsoTime(entry.started_at)}` : null,
    entry.finished_at ? `end ${formatIsoTime(entry.finished_at)}` : null,
    entry.duration_ms ? `dur ${formatDurationMs(entry.duration_ms)}` : active && entry.started_at ? `dur ${formatDurationMs(nowMs() - new Date(entry.started_at).getTime())}` : null,
    entry.attempts ? `attempts ${entry.attempts}` : null,
  ].filter(Boolean).join(' · ');

  return `<div style="padding:7px 0;border-top:1px solid rgba(255,255,255,.06)">
    <div style="display:flex;justify-content:space-between;gap:8px;align-items:center">
      <div style="font-weight:600">${escHtml(entry.action || entry.id || 'command')}</div>
      <span class="nst ${tone}">${escHtml(state)}</span>
    </div>
    <div style="color:var(--ink3);margin-top:2px">${escHtml(entry.endpoint || 'controller-ui')} · ${escHtml(timing || formatIsoTime(entry.ts || entry.updated_at || entry.started_at || nowIso()))}</div>
    <div style="color:var(--ink3);margin-top:2px">${escHtml(detail || (active ? 'Waiting for acknowledgement…' : 'No extra details'))}</div>
  </div>`;
}

function renderCommandLifecycle() {
  const activeHost = el('sweetie-command-active');
  const historyHost = el('sweetie-command-history');
  const summaryHost = el('sweetie-command-summary');
  if (!activeHost && !historyHost && !summaryHost) return;

  const active = Array.from(BRIDGE.activeCommands.values())
    .sort((a, b) => String(b.updated_at || '').localeCompare(String(a.updated_at || '')))
    .slice(0, ACTIVE_RENDER_LIMIT);
  const history = BRIDGE.commandHistory.slice(0, HISTORY_RENDER_LIMIT);

  if (summaryHost) {
    const latest = history[0];
    summaryHost.textContent = active.length
      ? `${active.length} active · ${history.length} recent`
      : latest
        ? `Last ${latest.status || 'event'} · ${formatIsoTime(latest.finished_at || latest.ts)}`
        : 'No active commands';
  }

  if (activeHost) {
    activeHost.innerHTML = active.length
      ? active.map(entry => renderCommandRow(entry, true)).join('')
      : 'No active commands.';
  }

  if (historyHost) {
    historyHost.innerHTML = history.length
      ? history.map(entry => renderCommandRow(entry, false)).join('')
      : 'No command history yet.';
  }
}

function renderOverviewBanner(summary) {
  return `<div class="node-row" style="display:block;padding:10px 12px;border:1px solid rgba(255,255,255,.08);border-radius:12px;background:rgba(255,255,255,.02)">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <span class="node-name" style="font-weight:700;flex:1">Sweetie integration overview</span>
      <span class="terrain-chip terrain-flat">online ${summary.onlinePlugins}/${summary.totalPlugins}</span>
      <span class="terrain-chip terrain-flat">compatible ${summary.compatiblePlugins}/${summary.totalPlugins}</span>
      <span class="terrain-chip terrain-flat">active cmds ${BRIDGE.activeCommands.size}</span>
      <span class="terrain-chip terrain-flat">history ${BRIDGE.commandHistory.length}</span>
    </div>
    <div style="font-size:11px;color:var(--ink3);margin-top:6px">Last refresh ${escHtml(summary.controller?.error || summary.controller?.stateSummary?.motion || summary.controller?.goal || summary.controller?.focus || BRIDGE.lastRefresh || 'unknown')}</div>
  </div>`;
}


function updateSummaryCards(summary) {
  const manifests = summary.plugins.filter(plugin => plugin.manifest).length;
  setText('sweetie-summary-online', `${summary.onlinePlugins} / ${summary.totalPlugins}`, summary.onlinePlugins ? 'ok' : 'warn');
  setText('sweetie-summary-compatible', `${summary.compatiblePlugins} / ${summary.totalPlugins}`, summary.compatiblePlugins ? 'ok' : 'warn');
  setText('sweetie-summary-manifests', String(manifests), manifests ? 'ok' : 'warn');
  setText('sweetie-summary-controller', summary.controller?.ok ? 'Ready' : summary.controller?.score >= 3 ? 'Partial' : 'Limited', summary.controller?.ok ? 'ok' : summary.controller?.score >= 3 ? 'warn' : 'err');

  const surfaces = summary.controller?.surfaces || {};
  setText('sweetie-surface-execute', surfaces.execute?.ok ? 'Ready' : surfaces.execute?.error || 'Missing', surfaces.execute?.ok ? 'ok' : 'err');
  setText('sweetie-surface-state', surfaces.state?.ok ? 'Ready' : surfaces.state?.error || 'Missing', surfaces.state?.ok ? 'ok' : 'err');
  setText('sweetie-surface-capabilities', surfaces.capabilities?.ok ? 'Ready' : surfaces.capabilities?.error || 'Missing', surfaces.capabilities?.ok ? 'ok' : 'warn');
  setText('sweetie-surface-stream', summary.controller?.streaming?.connected ? 'WS connected' : summary.controller?.streaming?.webSocket ? 'WS attached' : 'WS offline', summary.controller?.streaming?.connected ? 'ok' : 'warn');

  const family = summary.familySummary || {};
  setText('sweetie-status-autonomy-mode', formatStateValue(family.autonomy?.mode), family.autonomy?.mode ? 'ok' : 'warn');
  setText('sweetie-status-autonomy-goal', formatStateValue(family.autonomy?.goal || summary.controller?.goal), family.autonomy?.goal || summary.controller?.goal ? 'ok' : 'warn');
  setText('sweetie-status-best-friend', formatStateValue(family.social?.bestFriend), family.social?.bestFriend ? 'ok' : 'warn');
  setText('sweetie-status-social-focus', formatStateValue(family.social?.focus || summary.controller?.focus), family.social?.focus || summary.controller?.focus ? 'ok' : 'warn');
  setText('sweetie-status-battery', formatStateValue(family.battery?.level ?? summary.controller?.stateSummary?.battery), (family.battery?.level ?? summary.controller?.stateSummary?.battery) != null ? 'ok' : 'warn');
  setText('sweetie-status-dock', formatStateValue(family.battery?.dock || summary.controller?.docking || summary.controller?.stateSummary?.dock), (family.battery?.dock || summary.controller?.docking || summary.controller?.stateSummary?.dock) ? 'ok' : 'warn');
  setText('sweetie-status-peer', formatStateValue(family.peer?.state || summary.controller?.peerState), (family.peer?.state || summary.controller?.peerState) ? 'ok' : 'warn');
  setText('sweetie-status-adapters', `${summary.plugins.filter(p => /(Adapter)$/i.test(p.name) && p.online).length} / ${summary.plugins.filter(p => /(Adapter)$/i.test(p.name)).length}`, 'ok');

  const capNode = el('sweetie-capability-list');
  if (capNode) {
    capNode.innerHTML = renderCapabilityChips(Object.keys(BRIDGE.capabilities.merged || {}), 'No Sweetie capabilities detected yet');
  }

  const notes = [];
  if (!summary.controller?.surfaces?.execute?.ok) notes.push('Controller /execute is still missing or non-standard. Quick actions will fall back to direct plugin execute calls.');
  if (!summary.controller?.surfaces?.capabilities?.ok) notes.push('Controller /capabilities is missing, so contract discovery is relying on manifests/status payloads.');
  if (!summary.plugins.some(plugin => plugin.name === 'perceptionAdapter' && plugin.online)) notes.push('Perception adapter is offline; best-friend and world-target flows cannot be validated end-to-end.');
  if (!summary.plugins.some(plugin => plugin.name === 'batteryAdapter' && plugin.online)) notes.push('Battery adapter is offline; low-battery dock flow cannot be verified from the UI.');
  if (!summary.plugins.some(plugin => plugin.name === 'peerAdapter' && plugin.online)) notes.push('Peer adapter is offline; peer-status ping remains unverified.');
  if (!notes.length) notes.push('Controller exposes enough surfaces for the Sweetie integration pack to probe manifests, state, and execute paths.');
  const noteNode = el('sweetie-compat-notes');
  if (noteNode) noteNode.innerHTML = notes.map(note => `<div style="margin-bottom:6px">• ${escHtml(note)}</div>`).join('');
}

function renderPluginSidebar(summary) {
  const host = el('plugins-list');
  if (!host) return;

  const topPlugins = summary.plugins
    .slice()
    .sort((a, b) => (b.compatible - a.compatible) || (b.online - a.online) || (b.score - a.score))
    .slice(0, 8);

  const recentCommands = BRIDGE.commandHistory.slice(0, 4)
    .map(entry => `<div style="padding:6px 0;border-top:1px solid rgba(255,255,255,.06)"><div style="font-weight:600">${escHtml(entry.action || entry.id || 'command')}</div><div style="color:var(--ink3)">${escHtml(entry.status || 'unknown')} · ${escHtml(entry.endpoint || 'n/a')}</div></div>`)
    .join('');

  host.innerHTML = `
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-bottom:10px">
      <div class="node-row" style="padding:8px"><div style="font-size:11px;color:var(--ink3)">Online</div><div style="font-size:18px;font-weight:700">${summary.onlinePlugins}/${summary.totalPlugins}</div></div>
      <div class="node-row" style="padding:8px"><div style="font-size:11px;color:var(--ink3)">Compatible</div><div style="font-size:18px;font-weight:700">${summary.compatiblePlugins}/${summary.totalPlugins}</div></div>
      <div class="node-row" style="padding:8px"><div style="font-size:11px;color:var(--ink3)">Controller</div><div style="font-size:18px;font-weight:700">${summary.controller.ok ? 'Ready' : 'Partial'}</div></div>
      <div class="node-row" style="padding:8px"><div style="font-size:11px;color:var(--ink3)">Merged caps</div><div style="font-size:18px;font-weight:700">${summary.mergedCapabilityCount}</div></div>
    </div>
    <div style="font-size:11px;color:var(--ink3);margin-bottom:8px">Top responding plugin endpoints</div>
    ${topPlugins.map(plugin => `<div class="node-row" style="padding:8px;margin-bottom:6px"><div style="display:flex;justify-content:space-between;gap:8px"><span style="font-weight:600">${escHtml(titleizeKey(plugin.name))}</span><span class="nst ${plugin.compatible ? 'ok' : plugin.online ? 'warn' : 'err'}">${escHtml(plugin.statusText)}</span></div><div style="font-size:11px;color:var(--ink3);margin-top:4px">${escHtml(plugin.detail)}</div></div>`).join('') || '<div style="color:var(--ink3)">No plugin probes yet.</div>'}
    <div style="font-size:11px;color:var(--ink3);margin:10px 0 6px">Recent orchestrator activity</div>
    ${recentCommands || '<div style="color:var(--ink3)">No commands executed yet.</div>'}
  `;
}

function renderAll(summary) {
  updateSummaryCards(summary);
  const grid = el('sweetie-plugin-grid');
  if (!grid) return;
  grid.innerHTML = [
    renderOverviewBanner(summary),
    renderControllerSummary(summary.controller, summary),
    ...summary.plugins.map(renderPluginProbe),
  ].join('');
  renderPluginSidebar(summary);
  renderCommandLifecycle();
}

export function getSweetieBridge() {
  return BRIDGE;
}

export function initSweetieIntegration() {
  const host = el('sweetie-stack-config');
  const grid = el('sweetie-plugin-grid');
  if (!host || !grid) return;

  const cfg = BRIDGE.reloadCfg();
  host.innerHTML = Object.entries(cfg)
    .map(([key, value]) => row(titleizeKey(key), key, value))
    .join('');

  el('sweetie-save-btn')?.addEventListener('click', () => {
    BRIDGE.updateCfgFromDom();
    log('ok', 'Sweetie plugin endpoints saved');
  });

  el('sweetie-refresh-btn')?.addEventListener('click', refreshSweetieStatuses);
  el('sweetie-follow-btn')?.addEventListener('click', () => quickAction('follow_best_friend'));
  el('sweetie-patrol-btn')?.addEventListener('click', () => quickAction('patrol_basic'));
  el('sweetie-stop-btn')?.addEventListener('click', () => quickAction('safe_stop'));
  el('sweetie-dock-btn')?.addEventListener('click', () => quickAction('force_dock'));
  el('sweetie-clear-override-btn')?.addEventListener('click', () => quickAction('clear_autonomy_override'));
  el('sweetie-peer-ping-btn')?.addEventListener('click', () => quickAction('peer_status_ping'));

  setQuickActionState('Idle', 'ok');
  renderCommandLifecycle();
  refreshSweetieStatuses();
}

export async function refreshSweetieStatuses() {
  const grid = el('sweetie-plugin-grid');
  if (grid) {
    grid.innerHTML = '<div style="font-size:12px;color:var(--ink3)">Checking controller compatibility, capabilities, and Sweetie plugin health…</div>';
  }

  const summary = await BRIDGE.refresh();
  renderAll(summary);

  if (!summary.controller.ok) {
    log('warn', `Sweetie controller compatibility is partial (${summary.controller.score || 0}/7 surfaces)`);
  }
  log('info', `Sweetie refresh complete: ${summary.compatiblePlugins}/${summary.totalPlugins} compatible, ${summary.onlinePlugins} online`);
  return summary;
}

export async function quickAction(chainName) {
  const requested = QUICK_ACTIONS[chainName];
  const spec = requested?.aliasFor ? QUICK_ACTIONS[requested.aliasFor] : requested;
  if (!spec) {
    log('err', `Unknown Sweetie quick action: ${chainName}`);
    return;
  }

  if (spec.confirm && typeof window !== 'undefined' && typeof window.confirm === 'function') {
    const ok = window.confirm(spec.confirm);
    if (!ok) {
      log('warn', `Sweetie quick action '${chainName}' cancelled by operator`);
      setQuickActionState('Cancelled', 'warn');
      return;
    }
  }

  const cfg = BRIDGE.reloadCfg();
  const baseUrl = normalizeBaseUrl(cfg[spec.endpoint]);
  if (!baseUrl) {
    log('err', `No endpoint configured for ${spec.endpoint}`);
    return;
  }

  const probe = await BRIDGE.probePlugin(spec.endpoint, baseUrl);
  const actionSupported = !probe.capabilityList.length || spec.capabilityHints.some(cap => probe.capabilityList.includes(cap));
  if (!actionSupported) {
    log('warn', `Endpoint ${spec.endpoint} did not advertise ${spec.capabilityHints.join(', ')}`);
  }

  const standardEnvelope = buildExecuteEnvelope({
    plugin: probe.manifest?.name || spec.endpoint,
    action: spec.action,
    input: spec.input,
  });

  const commandId = standardEnvelope.request_id;
  setQuickActionState(`Running ${chainName}`, 'warn');
  BRIDGE.setActiveCommand(commandId, {
    id: commandId,
    action: spec.action,
    endpoint: spec.endpoint,
    status: 'queued',
  });

  renderCommandLifecycle();

  try {
    BRIDGE.markCommandAttempt(commandId, { id: commandId, action: spec.action, endpoint: `${spec.endpoint}:standard`, status: 'running', plugin: spec.endpoint, params: spec.input });
    renderCommandLifecycle();
    const data = await fetchJson(`${baseUrl}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(standardEnvelope),
    });
    BRIDGE.completeActiveCommand(commandId, data?.status || 'completed', data, null);
    renderCommandLifecycle();
    log('ok', `Sweetie quick action '${chainName}' sent via standard /execute envelope`);
    setQuickActionState(`Completed ${chainName}`, 'ok');
    console.log('Sweetie standard execute result', data);
    renderPluginSidebar(BRIDGE.lastSummary || await BRIDGE.refresh());
    return data;
  } catch (standardError) {
    try {
      BRIDGE.markCommandAttempt(commandId, { id: commandId, action: spec.action, endpoint: `${spec.endpoint}:legacy`, status: 'running', plugin: spec.endpoint, params: spec.input });
      renderCommandLifecycle();
      const legacy = await fetchJson(`${baseUrl}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildLegacyPayload(spec)),
      });
      BRIDGE.completeActiveCommand(commandId, legacy?.status || 'completed', legacy, null);
      renderCommandLifecycle();
      log('warn', `Sweetie quick action '${chainName}' used legacy execute payload: ${standardError.message}`);
      setQuickActionState(`Completed ${chainName} via legacy`, 'warn');
      console.log('Sweetie legacy execute result', legacy);
      renderPluginSidebar(BRIDGE.lastSummary || await BRIDGE.refresh());
      return legacy;
    } catch (legacyError) {
      BRIDGE.completeActiveCommand(commandId, 'failed', null, legacyError.message);
      renderCommandLifecycle();
      log('err', `Sweetie quick action failed: ${legacyError.message}`);
      setQuickActionState(`Failed ${chainName}`, 'err');
      renderPluginSidebar(BRIDGE.lastSummary || await BRIDGE.refresh());
      throw legacyError;
    }
  }
}

export const __sweetieTestHooks = {
  buildExecuteEnvelope,
  buildLegacyPayload,
  summarizeControllerState,
  summarizePluginFamilies,
  renderCommandLifecycle,
  formatDurationMs,
  formatIsoTime,
};

window.SweetieBridge = BRIDGE;
