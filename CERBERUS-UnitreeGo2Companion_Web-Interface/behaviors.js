/**
 * behaviors.js — Behaviors, Objects, Missions tabs + Plugin panel.
 *
 * i18n functions have moved to i18n.js.
 *
 * Element IDs used (must match index.html):
 *   #beh-grid       — behavior card grid
 *   #cat-pills      — category filter bar
 *   #obj-grid       — objects list
 *   #mission-list   — missions list
 *   #plugins-list   — plugin roster
 *   Add-object modal: #ao-id, #ao-name, #ao-type, #ao-aff, #ao-moods, #ao-force
 */

import { P, el, log }                from './config.js';
import { apiFetch, apiCmd, apiPost } from './api.js';
import { EP }                        from './config.js';

// ── Behaviors ─────────────────────────────────────────────────────────────────

export async function loadBehaviors() {
  try {
    const r  = await apiFetch('/api/v1/behaviors');
    P.behaviors = r.behaviors || [];
  } catch (_) { /* use simulation.js built-ins */ }
  renderBehaviors();
}

export function renderBehaviors() {
  _renderCatPills();

  const grid = el('beh-grid'); if (!grid) return;
  const list = P.selCat === 'all'
    ? P.behaviors
    : P.behaviors.filter(b => b.category === P.selCat);

  grid.innerHTML = list.map(b =>
    `<div class="beh-btn ${b._running ? 'running' : ''}" onclick="window.runBeh('${b.id}')">
       <div class="beh-ico">${b.icon || '🐾'}</div>
       <div class="beh-name">${b.name}</div>
       ${b.duration_s ? `<div class="beh-cat">${b.duration_s}s</div>` : ''}
     </div>`
  ).join('');
}

/** Rebuild category pill bar from current P.behaviors data. */
function _renderCatPills() {
  const bar = el('cat-pills'); if (!bar) return;
  const cats = ['all', ...new Set(P.behaviors.map(b => b.category).filter(Boolean))];
  bar.innerHTML = cats.map(cat =>
    `<div class="cpill ${P.selCat === cat ? 'active' : ''}"
          onclick="window.filterCat('${cat}',this)">${cat}</div>`
  ).join('');
}

export function filterCat(cat, catEl) {
  P.selCat = cat;
  document.querySelectorAll('.cpill').forEach(e => e.classList.remove('active'));
  catEl?.classList.add('active');
  renderBehaviors();
}

export function runBeh(id) {
  _markRunning(id);
  apiCmd('RUN_BEHAVIOR', { behavior_id: id });
}

function _markRunning(id) {
  const b = P.behaviors.find(b => b.id === id); if (!b) return;
  b._running = true;
  renderBehaviors();
  setTimeout(() => { b._running = false; renderBehaviors(); }, (b.duration_s ?? 2) * 1000);
}

// ── Objects ───────────────────────────────────────────────────────────────────

export async function loadObjects() {
  try {
    const r = await apiFetch('/api/v1/objects');
    P.objects = Array.isArray(r) ? r : r.objects || [];
  } catch (_) {}
  renderObjects();
}

export function renderObjects() {
  const grid = el('obj-grid'); if (!grid) return;
  grid.innerHTML = P.objects.map((o, i) =>
    `<div class="card" style="cursor:pointer;border:2px solid ${P.selObj === i ? 'var(--amber)' : 'transparent'}"
          onclick="window.selObj(${i})">
       <div style="font-weight:600;font-size:13px">${o.name}</div>
       <div style="font-size:11px;color:var(--ink3)">${o.type || 'prop'}</div>
       ${o.affordances?.length ? `<div style="font-size:10px;color:var(--ink3);margin-top:4px">${o.affordances.join(', ')}</div>` : ''}
     </div>`
  ).join('');
}

export function selObj(i) {
  P.selObj = i;
  renderObjects();
  const o = P.objects[i]; if (!o) return;
  apiCmd('SET_TARGET', { object: o });
  log('ok', 'Target: ' + o.name);
}

export function openAddObj()  { const m = el('add-obj-modal'); if (m) m.style.display = 'flex'; }
export function closeAddObj() { const m = el('add-obj-modal'); if (m) m.style.display = 'none'; }

export async function submitAddObj() {
  const name  = el('ao-name')?.value?.trim();
  const type  = el('ao-type')?.value?.trim() || 'generic';
  const affRaw= el('ao-aff')?.value?.trim() || '';
  const force = parseFloat(el('ao-force')?.value || '20');
  const objId = el('ao-id')?.value?.trim() || 'obj_' + Date.now();

  if (!name) { log('warn', 'Object name required'); return; }

  const obj = {
    id: objId, name, type,
    affordances: affRaw ? affRaw.split(',').map(s => s.trim()).filter(Boolean) : [],
    moods: [],
    max_force_n: force,
  };

  if (P.connected) {
    try { await apiPost('/api/v1/objects', obj); await loadObjects(); }
    catch (e) { log('err', 'Add object: ' + e.message); return; }
  } else {
    P.objects.push(obj);
    renderObjects();
  }
  closeAddObj();
  log('ok', 'Object added: ' + name);
}

export function exportObjs() {
  const a   = document.createElement('a');
  a.href     = 'data:application/json,' + encodeURIComponent(JSON.stringify(P.objects, null, 2));
  a.download = 'cerberus-objects.json';
  a.click();
}

export function importObjs()       { el('obj-import-input')?.click(); }

export function handleObjImport(e) {
  const file = e.target?.files?.[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      const data = JSON.parse(ev.target.result);
      P.objects = Array.isArray(data) ? data : [];
      renderObjects();
      log('ok', `Imported ${P.objects.length} objects`);
    } catch (_) { log('err', 'Invalid object file — expected JSON array'); }
  };
  reader.readAsText(file);
}

// ── Missions ──────────────────────────────────────────────────────────────────

export async function loadMissions() {
  try {
    const r = await apiFetch('/api/v1/missions');
    P.missions = Array.isArray(r) ? r : r.missions || [];
  } catch (_) {}
  renderMissions();
}

export function renderMissions() {
  const list = el('mission-list'); if (!list) return;
  list.innerHTML = P.missions.map(m =>
    `<div class="card" style="display:flex;align-items:center;gap:10px">
       <div style="flex:1">
         <div style="font-weight:600;font-size:13px">${m.name}</div>
         <div style="font-size:11px;color:var(--ink3)">${m.type || 'patrol'}</div>
       </div>
       <div class="tval ${m.status === 'running' ? 'ok' : ''}" style="font-size:11px">${m.status || 'pending'}</div>
       <div style="font-size:11px;color:var(--ink3);min-width:32px">${Math.round((m.progress || 0) * 100)}%</div>
       <button class="btn btn-p" style="padding:4px 10px;font-size:11px"
               onclick="window.startMission('${m.id}')">▶</button>
     </div>`
  ).join('');
}

export async function createMission() {
  const name = el('m-name')?.value?.trim();
  const type = el('m-type')?.value || 'patrol';
  if (!name) { log('warn', 'Mission name required'); return; }
  const mission = { id: 'ms_' + Date.now(), name, type, status: 'pending', progress: 0 };
  P.missions.push(mission);
  renderMissions();
  log('ok', 'Mission created: ' + name);
}

export async function startMission(id) {
  if (P.connected) {
    try { await apiPost('/api/v1/missions/' + id + '/start'); }
    catch (e) { log('err', 'Mission start: ' + e.message); return; }
  }
  const m = P.missions.find(m => m.id === id);
  if (m) { m.status = 'running'; renderMissions(); }
  log('ok', 'Mission started: ' + id);
}

export async function stopMission() {
  if (P.connected) {
    try { await apiPost('/api/v1/missions/active/stop'); }
    catch (e) { log('err', 'Mission stop: ' + e.message); return; }
  }
  P.missions.forEach(m => { if (m.status === 'running') m.status = 'stopped'; });
  renderMissions();
  log('warn', 'Mission stopped');
}

// ── Plugins ───────────────────────────────────────────────────────────────────

export function renderPlugins(plugins) {
  const list = el('plugins-list'); if (!list) return;
  if (!plugins?.length) {
    list.textContent = 'No plugins loaded.';
    return;
  }
  list.innerHTML = plugins.map(p =>
    `<div class="node-row" style="align-items:center;gap:6px">
       <span class="node-name" style="flex:1">${p.name}</span>
       <span class="nst ${p.enabled ? 'ok' : ''}">${p.enabled ? 'active' : 'off'}</span>
       <button class="btn btn-ghost" style="padding:2px 8px;font-size:10px"
               onclick="window.enablePlugin('${p.name}')">ON</button>
       <button class="btn btn-ghost" style="padding:2px 8px;font-size:10px"
               onclick="window.disablePlugin('${p.name}')">OFF</button>
     </div>`
  ).join('');
}

export async function enablePlugin(name) {
  try { await apiPost(EP.plugins + '/' + name + '/enable'); await _refreshPlugins(); }
  catch (e) { log('err', 'Enable plugin: ' + e.message); }
}

export async function disablePlugin(name) {
  try { await apiPost(EP.plugins + '/' + name + '/disable'); await _refreshPlugins(); }
  catch (e) { log('err', 'Disable plugin: ' + e.message); }
}

async function _refreshPlugins() {
  try { P.plugins = await apiFetch(EP.plugins); renderPlugins(P.plugins); }
  catch (_) {}
}
