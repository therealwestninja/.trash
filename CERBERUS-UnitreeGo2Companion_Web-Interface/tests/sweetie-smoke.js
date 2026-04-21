import { P } from '../config.js';
import { initSweetieIntegration, refreshSweetieStatuses, quickAction, getSweetieBridge } from '../sweetie.js';

const out = document.getElementById('results');
const lines = [];
function note(text, cls = '') {
  lines.push(`<div class="${cls}">${text}</div>`);
  out.innerHTML = lines.join('');
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
  note(`PASS: ${message}`, 'ok');
}

window.confirm = () => true;
P.apiBase = 'http://controller.test';
P.connected = true;
P.ws = {};
localStorage.setItem('sweetie_controller_endpoints_v4', JSON.stringify({
  autonomySupervisor: 'http://sweetie.test/autonomy',
  batteryAdapter: 'http://sweetie.test/battery',
  peerAdapter: 'http://sweetie.test/peer',
  socialBonding: 'http://sweetie.test/social',
  perceptionAdapter: 'http://sweetie.test/perception',
  motionAdapter: 'http://sweetie.test/motion',
  audioAdapter: 'http://sweetie.test/audio',
  eventBus: 'http://sweetie.test/event',
  actionRegistry: 'http://sweetie.test/action-registry',
  gaitLibrary: 'http://sweetie.test/gaits',
  crusaderLink: 'http://sweetie.test/crusader'
}));

const pluginNames = {
  autonomy: { mode: 'follow_best_friend', goal: 'shadow-operator', manual_override: false },
  battery: { battery_pct: 91, dock_state: 'undocked', charging: false },
  peer: { peer_state: 'online', transport: 'wifi', peer_count: 1 },
  social: { best_friend: 'operator-001', focus_target: 'operator-001', bond_state: 'bonded' },
  perception: { source: 'camera', state: 'tracking' },
  motion: { state: 'standing' },
  audio: { state: 'idle' },
  event: { state: 'ready' },
  'action-registry': { state: 'ready' },
  gaits: { state: 'ready' },
  crusader: { state: 'ready' },
};

const executeAttempts = { standard: 0, legacy: 0 };

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } });
}

window.fetch = async (url, options = {}) => {
  const method = (options.method || 'GET').toUpperCase();
  const body = options.body ? JSON.parse(options.body) : null;

  if (url === 'http://controller.test/execute' && method === 'OPTIONS') {
    return jsonResponse({ allow: ['POST', 'OPTIONS'] });
  }
  if (url === 'http://controller.test/state') {
    return jsonResponse({ battery_pct: 88, motion_state: 'ready', docking_state: 'clear', peer_state: 'online' });
  }
  if (url === 'http://controller.test/capabilities') {
    return jsonResponse({ capabilities: ['controller.execute', 'controller.state'] });
  }
  if (url === 'http://controller.test/session') {
    return jsonResponse({ session_id: 'smoke-session' });
  }
  if (url === 'http://controller.test/behavior') {
    return jsonResponse({ current_goal: 'shadow-operator', focus_target: 'operator-001' });
  }
  if (url === 'http://controller.test/plugins') {
    return jsonResponse({ plugins: ['sweetie'] });
  }
  if (url === 'http://controller.test/terrain') {
    return jsonResponse({ terrain: 'flat' });
  }

  if (url.startsWith('http://sweetie.test/')) {
    const [, host, service, path] = url.match(/^http:\/\/sweetie\.test\/([^/]+)(?:\/(.*))?$/) || [];
    if (!host) throw new Error(`Unhandled plugin URL: ${url}`);
    const state = pluginNames[host] || { state: 'ready' };
    const pluginLabel = host === 'autonomy' ? 'autonomySupervisor' : host;
    if (!path || path === 'health') return jsonResponse({ ok: true, plugin: pluginLabel, version: '0.4.0-smoke' });
    if (path === 'manifest') {
      return jsonResponse({
        name: pluginLabel,
        version: '0.4.0-smoke',
        capabilities: host === 'autonomy' ? ['autonomy.execute', 'autonomy.override.clear'] : ['status.read'],
        entrypoints: { execute: '/execute', status: '/status', health: '/health' },
      });
    }
    if (path === 'status') return jsonResponse({ ...state, version: '0.4.0-smoke' });
    if (path === 'execute' && method === 'POST') {
      if (body && body.request_id) {
        executeAttempts.standard += 1;
        return jsonResponse({ detail: 'standard envelope not enabled in smoke mode' }, 400);
      }
      executeAttempts.legacy += 1;
      return jsonResponse({ status: 'completed', accepted: true, mode: body?.payload?.mode || body?.payload?.resume_policy || 'ok' });
    }
  }

  throw new Error(`Unhandled fetch route: ${method} ${url}`);
};

(async () => {
  try {
    note('Running smoke test…', 'warn');
    initSweetieIntegration();
    await refreshSweetieStatuses();

    assert(document.getElementById('sweetie-summary-controller').textContent.includes('Ready'), 'controller readiness summary renders');
    assert(document.getElementById('sweetie-status-best-friend').textContent.includes('operator-001'), 'best-friend summary renders');
    assert(document.getElementById('sweetie-capability-list').textContent.includes('controller.execute'), 'merged capabilities render');

    await quickAction('follow_best_friend');
    const bridge = getSweetieBridge();
    assert(executeAttempts.standard === 1, 'standard execute path attempted first');
    assert(executeAttempts.legacy === 1, 'legacy execute fallback attempted after standard failure');
    assert(bridge.commandHistory.some(entry => entry.status === 'failed_attempt'), 'failed attempt recorded in lifecycle history');
    assert(document.getElementById('sweetie-command-history').textContent.includes('follow_best_friend') || document.getElementById('sweetie-command-history').textContent.includes('autonomy.execute'), 'command lifecycle history renders');
    assert(document.getElementById('sweetie-quick-action-status').textContent.includes('Completed'), 'quick action status renders completion');

    note('Smoke test completed successfully.', 'ok');
  } catch (error) {
    note(`FAIL: ${error.message}`, 'fail');
    console.error(error);
  }
})();
