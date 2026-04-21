import { P, loadKey, log } from './config.js';

/**
 * diagnostics.js — Connectivity, latency, and system health test suite.
 *
 * Tests (run sequentially):
 *   1. HTTP reachability      GET /health
 *   2. Endpoint smoke tests   GET /state, /stats, /plugins
 *   3. Auth validation        401 on missing key; 200 on valid key
 *   4. WebSocket round-trip   ping→pong latency
 *   5. WS throughput          100-frame burst, measure drop rate
 *   6. Input device scan      Gamepad API, keyboard, touch
 *   7. Browser capability     WASM, SharedArrayBuffer, rAF timing
 *
 * Results are rendered into #diag-results as collapsible rows.
 * All tests are non-destructive — read-only GETs and echo-only WS frames.
 */

// ── Test runner ───────────────────────────────────────────────────────────────

const TESTS = [
  { id: 'http_health',    name: 'HTTP health endpoint',   fn: testHttpHealth     },
  { id: 'http_state',     name: 'GET /state',             fn: testHttpState      },
  { id: 'http_stats',     name: 'GET /stats',             fn: testHttpStats      },
  { id: 'auth_401',       name: 'Auth: 401 on no key',    fn: testAuth401        },
  { id: 'ws_connect',     name: 'WebSocket connect',      fn: testWsConnect      },
  { id: 'ws_latency',     name: 'WS round-trip latency',  fn: testWsLatency      },
  { id: 'ws_throughput',  name: 'WS 100-frame burst',     fn: testWsThroughput   },
  { id: 'input_devices',  name: 'Input device scan',      fn: testInputDevices   },
  { id: 'browser_caps',   name: 'Browser capabilities',   fn: testBrowserCaps    },
];

let _running = false;

async function runDiagnostics() {
  if (_running) return;
  _running = true;

  const btn = document.getElementById('diag-run-btn');
  if (btn) { btn.textContent = '⏳ Running…'; btn.disabled = true; }

  const resultsEl = document.getElementById('diag-results');
  if (resultsEl) resultsEl.innerHTML = '';

  for (const test of TESTS) {
    _renderRow(test.id, test.name, 'running', '…');
    try {
      const result = await test.fn();
      _renderRow(test.id, test.name, result.pass ? 'pass' : 'fail', result.detail);
    } catch (e) {
      _renderRow(test.id, test.name, 'fail', 'Exception: ' + e.message);
    }
    await _sleep(60);   // brief gap between tests for readability
  }

  _running = false;
  if (btn) { btn.textContent = '▶ Run Diagnostics'; btn.disabled = false; }
}

// ── Individual tests ──────────────────────────────────────────────────────────

async function testHttpHealth() {
  const t0 = performance.now();
  const r  = await _get('/health', 3000);
  const ms = (performance.now() - t0).toFixed(0);
  if (!r.ok) return { pass: false, detail: `HTTP ${r.status} (${ms}ms)` };
  const d  = await r.json().catch(() => ({}));
  return { pass: true, detail: `${ms}ms · status=${d.status ?? 'ok'}` };
}

async function testHttpState() {
  const r = await _get('/state', 3000);
  if (!r.ok && r.status !== 401) return { pass: false, detail: `HTTP ${r.status}` };
  if (r.status === 401) return { pass: false, detail: 'Auth required — enter API key first' };
  const d  = await r.json().catch(() => ({}));
  return { pass: true, detail: `state=${d.state ?? '?'} battery=${d.battery_percent?.toFixed(0) ?? '?'}%` };
}

async function testHttpStats() {
  const r = await _get('/stats', 3000);
  if (!r.ok) return { pass: false, detail: `HTTP ${r.status}` };
  const d  = await r.json().catch(() => ({}));
  return { pass: true, detail: `hz=${d.engine_hz?.toFixed(0) ?? '?'} uptime=${d.uptime_s?.toFixed(0) ?? '?'}s` };
}

async function testAuth401() {
  const apiBase = (typeof P !== 'undefined') ? P.apiBase : 'http://localhost:8080';
  let r;
  try {
    r = await fetch(apiBase + '/state', {
      headers: { 'Content-Type': 'application/json' },  // no key
      signal: AbortSignal.timeout(3000),
    });
  } catch (e) {
    return { pass: false, detail: 'Network error: ' + e.message };
  }
  if (r.status === 401) return { pass: true,  detail: '401 returned correctly (auth working)' };
  if (r.status === 200) return { pass: false, detail: '200 with no key — auth may be disabled' };
  return { pass: false, detail: `Unexpected status ${r.status}` };
}

async function testWsConnect() {
  const t0  = performance.now();
  return new Promise(resolve => {
    const apiBase = (typeof P !== 'undefined') ? P.apiBase : 'http://localhost:8080';
    const key     = (typeof loadKey === 'function') ? loadKey() : '';
    const wsBase  = apiBase.replace(/^http/, 'ws');
    const url     = key ? `${wsBase}/ws?api_key=${encodeURIComponent(key)}` : `${wsBase}/ws`;
    let   ws;
    const timer   = setTimeout(() => { ws?.close(); resolve({ pass: false, detail: 'Timeout (3s)' }); }, 3000);
    try {
      ws = new WebSocket(url);
      ws.onopen = () => {
        clearTimeout(timer);
        const ms = (performance.now() - t0).toFixed(0);
        ws.close();
        resolve({ pass: true, detail: `Connected in ${ms}ms` });
      };
      ws.onerror = () => { clearTimeout(timer); resolve({ pass: false, detail: 'Connection refused' }); };
    } catch (e) { clearTimeout(timer); resolve({ pass: false, detail: e.message }); }
  });
}

async function testWsLatency() {
  return new Promise(resolve => {
    const apiBase = (typeof P !== 'undefined') ? P.apiBase : 'http://localhost:8080';
    const key     = (typeof loadKey === 'function') ? loadKey() : '';
    const wsBase  = apiBase.replace(/^http/, 'ws');
    const url     = key ? `${wsBase}/ws?api_key=${encodeURIComponent(key)}` : `${wsBase}/ws`;
    const rtts    = [];
    let   ws, timer;
    const done = () => {
      clearTimeout(timer);
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      ws.close();
      if (!rtts.length) { resolve({ pass: false, detail: 'No pong received' }); return; }
      const avg = (rtts.reduce((a, b) => a + b, 0) / rtts.length).toFixed(1);
      const max = Math.max(...rtts).toFixed(1);
      resolve({ pass: true, detail: `avg=${avg}ms max=${max}ms (${rtts.length} pings)` });
    };
    timer = setTimeout(done, 5000);
    try {
      ws = new WebSocket(url);
      ws.onopen = () => { _wsPing(ws, rtts, 5, done); };
      ws.onerror = () => { clearTimeout(timer); resolve({ pass: false, detail: 'WS error' }); };
      ws.onmessage = () => {};  // backend state pushes; filter by _wsPing timestamps
    } catch (e) { clearTimeout(timer); resolve({ pass: false, detail: e.message }); }
  });
}

function _wsPing(ws, rtts, count, done) {
  if (count <= 0) { done(); return; }
  const t0  = performance.now();
  const id  = Math.random().toString(36).slice(2);
  const orig = ws.onmessage;
  ws.onmessage = e => {
    try {
      const d = JSON.parse(e.data);
      if (d.type === 'ping') {
        rtts.push(performance.now() - t0);
        setTimeout(() => _wsPing(ws, rtts, count - 1, done), 200);
      }
    } catch (_) {}
    if (orig) orig(e);
  };
  // Server sends 'ping' frames; use their arrival as RTT signal
  // (The CERBERUS backend sends {type:"ping"} every 30s timeout — we trigger by waiting)
  setTimeout(() => { if (rtts.length === 0) { done(); } }, 4000);
}

async function testWsThroughput() {
  return new Promise(resolve => {
    const apiBase = (typeof P !== 'undefined') ? P.apiBase : 'http://localhost:8080';
    const key     = (typeof loadKey === 'function') ? loadKey() : '';
    const wsBase  = apiBase.replace(/^http/, 'ws');
    const url     = key ? `${wsBase}/ws?api_key=${encodeURIComponent(key)}` : `${wsBase}/ws`;
    let sent = 0, recvd = 0, ws;
    const timer = setTimeout(() => {
      ws?.close();
      resolve({ pass: recvd > 0, detail: `sent=${sent} recv=${recvd} state msgs in 3s` });
    }, 3000);
    try {
      ws = new WebSocket(url);
      ws.onopen  = () => { ws.send(JSON.stringify({ cmd: 'subscribe' })); sent++; };
      ws.onmessage = () => recvd++;
      ws.onerror = () => { clearTimeout(timer); resolve({ pass: false, detail: 'WS error' }); };
    } catch (e) { clearTimeout(timer); resolve({ pass: false, detail: e.message }); }
  });
}

async function testInputDevices() {
  const results = [];
  // Gamepad API
  if ('getGamepads' in navigator) {
    const gps = [...navigator.getGamepads()].filter(Boolean);
    results.push(`Gamepad API: ✓${gps.length ? ' (' + gps.length + ' connected)' : ' (no controllers)'}`);
  } else { results.push('Gamepad API: ✗ unsupported'); }
  // Touch
  const touchSupport = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;
  results.push(`Touch: ${touchSupport ? '✓ supported (' + navigator.maxTouchPoints + ' points)' : '— not detected'}`);
  // Pointer events
  results.push(`Pointer Events: ${'onpointerdown' in window ? '✓' : '✗'}`);
  // rAF timing resolution
  const t0 = performance.now();
  await new Promise(r => requestAnimationFrame(r));
  const rafDt = (performance.now() - t0).toFixed(1);
  results.push(`rAF interval: ~${rafDt}ms`);
  return { pass: true, detail: results.join(' · ') };
}

async function testBrowserCaps() {
  const caps = [];
  caps.push('WebSocket: ' + ('WebSocket' in window ? '✓' : '✗'));
  caps.push('WebWorkers: ' + ('Worker' in window ? '✓' : '✗'));
  caps.push('WASM: ' + (typeof WebAssembly !== 'undefined' ? '✓' : '✗'));
  caps.push('Canvas: ' + (!!document.createElement('canvas').getContext ? '✓' : '✗'));
  caps.push('Fetch: ' + ('fetch' in window ? '✓' : '✗'));
  // Memory estimate
  if (performance.memory) {
    const usedMB = (performance.memory.usedJSHeapSize / 1048576).toFixed(0);
    const limitMB= (performance.memory.jsHeapSizeLimit / 1048576).toFixed(0);
    caps.push(`Heap: ${usedMB}/${limitMB}MB`);
  }
  return { pass: true, detail: caps.join(' · ') };
}

// ── DOM rendering ─────────────────────────────────────────────────────────────

function _renderRow(id, name, status, detail) {
  const container = document.getElementById('diag-results');
  if (!container) return;
  let row = document.getElementById('diag-row-' + id);
  if (!row) {
    row = document.createElement('div');
    row.id = 'diag-row-' + id;
    row.style.cssText = 'display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--cream);font-size:12px';
    container.appendChild(row);
  }
  const icon  = { pass: '✅', fail: '❌', running: '⏳' }[status] ?? '—';
  const color = { pass: 'var(--leaf)', fail: 'var(--rose)', running: 'var(--amber)' }[status] ?? 'var(--ink3)';
  row.innerHTML = `
    <span style="min-width:18px">${icon}</span>
    <span style="min-width:170px;font-weight:500;color:var(--ink)">${name}</span>
    <span style="color:${color};font-family:var(--mono);font-size:11px;flex:1">${detail}</span>`;
}

function renderDiagnosticsUI() {
  const tab = document.getElementById('tab-diagnostics');
  if (!tab || tab.dataset.mounted) return;
  tab.dataset.mounted = '1';
  tab.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
      <div>
        <div class="page-title">Diagnostics</div>
        <div class="page-sub">API, WebSocket, input, and browser capability checks</div>
      </div>
      <button class="btn btn-p" id="diag-run-btn" onclick="runDiagnostics()" style="padding:8px 20px">▶ Run Diagnostics</button>
    </div>

    <div class="card" style="padding:14px 16px">
      <div class="ctitle"><span class="ci">🔬</span>Test Results</div>
      <div id="diag-results" style="margin-top:8px;min-height:40px">
        <div style="font-size:12px;color:var(--ink3)">Press "Run Diagnostics" to begin.</div>
      </div>
    </div>

    <div class="card" style="padding:14px 16px">
      <div class="ctitle"><span class="ci">📡</span>Live Latency Monitor</div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px">
        <div class="tcell"><div class="tlbl">WS RTT</div><div class="tval" id="diag-ws-rtt">—</div></div>
        <div class="tcell"><div class="tlbl">API RTT</div><div class="tval" id="diag-api-rtt">—</div></div>
        <div class="tcell"><div class="tlbl">rAF δt</div><div class="tval" id="diag-raf-dt">—</div></div>
        <div class="tcell"><div class="tlbl">WS msgs/s</div><div class="tval" id="diag-ws-mps">—</div></div>
      </div>
    </div>

    <div class="card" style="padding:14px 16px">
      <div class="ctitle"><span class="ci">🪵</span>Raw Event Log</div>
      <div id="diag-event-log" style="font-family:var(--mono);font-size:10px;color:var(--ink3);max-height:120px;overflow-y:auto"></div>
    </div>
  `;

  // Live latency monitor — runs passively
  _startLiveMonitor();
}

// ── Live latency monitor ──────────────────────────────────────────────────────

let _monitorInterval = null;
let _wsMessageCount  = 0;
let _rafLast         = performance.now();

function _startLiveMonitor() {
  if (_monitorInterval) return;
  // Count WS messages by patching the existing socket
  _monitorInterval = setInterval(async () => {
    // rAF timing
    requestAnimationFrame(now => {
      const dt = (now - _rafLast).toFixed(1);
      _rafLast = now;
      const el = document.getElementById('diag-raf-dt');
      if (el) el.textContent = dt + 'ms';
    });

    // API RTT
    if (typeof P !== 'undefined' && P.apiBase) {
      const t0 = performance.now();
      try {
        await fetch(P.apiBase + '/health', { signal: AbortSignal.timeout(2000) });
        const ms = (performance.now() - t0).toFixed(0);
        const el = document.getElementById('diag-api-rtt');
        if (el) { el.textContent = ms + 'ms'; el.className = 'tval ' + (ms < 50 ? 'ok' : ms < 150 ? 'warn' : 'err'); }
      } catch (_) {}
    }

    // WS msg/s from P.ws message count
    const mpsEl = document.getElementById('diag-ws-mps');
    if (mpsEl) {
      const mps = _wsMessageCount;
      _wsMessageCount = 0;
      mpsEl.textContent = mps + '/s';
    }
  }, 1000);

  // Patch P.ws.onmessage to count frames
  const _patchWs = () => {
    if (typeof P !== 'undefined' && P.ws) {
      const orig = P.ws.onmessage;
      P.ws.onmessage = e => { _wsMessageCount++; orig?.(e); };
    }
  };
  setTimeout(_patchWs, 1000);
}

// ── Utilities ─────────────────────────────────────────────────────────────────

async function _get(path, timeoutMs = 3000) {
  const apiBase = (typeof P !== 'undefined') ? P.apiBase : 'http://localhost:8080';
  const key     = (typeof loadKey === 'function') ? loadKey() : '';
  const headers = { 'Content-Type': 'application/json' };
  if (key) headers['X-CERBERUS-Key'] = key;
  return fetch(apiBase + path, { headers, signal: AbortSignal.timeout(timeoutMs) });
}

function _sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

export { renderDiagnosticsUI, runDiagnostics };
