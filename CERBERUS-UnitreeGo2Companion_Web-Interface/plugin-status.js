/**
 * plugin-status.js — Display handlers for CERBERUS plugin state events.
 *
 * Handles: payload, limb_loss, stair.
 * Each function is registered on window by main.js and called by ws.js
 * when the corresponding WS message type arrives.
 *
 * DOM elements written to are optional — absent elements are silently skipped.
 * This means the index.html can add these badges incrementally without
 * breaking anything if they're missing.
 *
 * Badge element IDs expected in index.html (add when ready):
 *   #payload-badge    — payload attach/drag state
 *   #limb-loss-badge  — limb loss / recovery state
 *   #stair-badge      — stair detection / climb state
 *   #stair-info       — metrics-tab text detail for stair
 */

import { P, el, log } from './config.js';

const READINESS_HOST_ID = 'plugins-controller-readiness';
const COMMAND_LOG_HOST_ID = 'plugins-command-log';
const CAPABILITY_HOST_ID = 'sweetie-capability-list';
const NOTES_HOST_ID = 'sweetie-compat-notes';

function escHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function compactJson(value, max = 60) {
  try {
    const raw = typeof value === 'string' ? value : JSON.stringify(value);
    return raw.length > max ? `${raw.slice(0, Math.max(0, max - 1))}…` : raw;
  } catch {
    return String(value ?? '');
  }
}

function getSweetieBridge() {
  return window.SweetieBridge || null;
}

function ensurePluginSignalState() {
  if (!P.pluginSignals || typeof P.pluginSignals !== 'object') {
    P.pluginSignals = {
      stair: null,
      payload: null,
      limbLoss: null,
      updatedAt: null,
    };
  }
  return P.pluginSignals;
}

function noteSignal(type, payload) {
  const state = ensurePluginSignalState();
  state[type] = payload;
  state.updatedAt = new Date().toISOString();

  const bridge = getSweetieBridge();
  if (bridge?.state?.plugins) {
    bridge.state.plugins[type] = payload;
    bridge.state.lastUpdated = state.updatedAt;
  }
}

function summarizeSignals() {
  const signals = ensurePluginSignalState();
  const stair = signals.stair;
  const payload = signals.payload;
  const limbLoss = signals.limbLoss;

  const stairActive = !!(stair && (stair.status === 'climbing' || stair.event === 'stair.detected'));
  const payloadDrag = !!(payload && payload.drag_warning);
  const payloadAttached = !!(payload && (payload.attached ?? (payload.event === 'payload.attached')));
  const lostLimbs = Array.isArray(limbLoss?.limbs_lost) ? limbLoss.limbs_lost : [];
  const limbRecovery = !!(limbLoss && (limbLoss.recovered || limbLoss.event === 'limb_loss.cleared'));
  const limbActive = lostLimbs.length > 0 && !limbRecovery;

  return {
    stairActive,
    payloadDrag,
    payloadAttached,
    limbActive,
    limbRecovery,
    lostLimbs,
    stairDirection: stair?.direction || null,
    stairProgress: stair?.status === 'climbing'
      ? `${stair.step ?? '?'} / ${stair.step_count ?? '?'}`
      : stair?.event === 'stair.detected'
        ? (stair.direction || 'detected')
        : null,
    payloadText: payloadDrag
      ? `drag ${payload.direction ?? ''}`.trim()
      : payloadAttached
        ? 'attached'
        : payload
          ? 'detached'
          : null,
    updatedAt: signals.updatedAt,
  };
}

function renderCompatibilityNotes() {
  const notesHost = el(NOTES_HOST_ID);
  const capHost = el(CAPABILITY_HOST_ID);
  const readinessHost = el(READINESS_HOST_ID);
  const commandHost = el(COMMAND_LOG_HOST_ID);

  if (!notesHost && !capHost && !readinessHost && !commandHost) return;

  const bridge = getSweetieBridge();
  const summary = summarizeSignals();
  const notes = [];
  const capabilityChips = [];

  capabilityChips.push('stair.detect');
  capabilityChips.push('payload.monitor');
  capabilityChips.push('recovery.limb_loss');

  if (summary.stairActive) {
    notes.push(`Stair plugin active${summary.stairDirection ? ` (${summary.stairDirection})` : ''}${summary.stairProgress ? ` — ${summary.stairProgress}` : ''}.`);
    capabilityChips.push('motion.stair_assist');
  }

  if (summary.payloadAttached || summary.payloadDrag) {
    notes.push(`Payload status: ${summary.payloadText}.`);
    capabilityChips.push(summary.payloadDrag ? 'payload.drag_warning' : 'payload.attached');
  }

  if (summary.limbActive) {
    notes.push(`Recovery active for ${summary.lostLimbs.join(', ')}.`);
    capabilityChips.push('motion.recovery_gait');
  } else if (summary.limbRecovery) {
    notes.push('Limb recovery confirmed.');
    capabilityChips.push('recovery.confirmed');
  }

  if (!notes.length) {
    notes.push('Plugin event channels are quiet. Waiting for stair, payload, or limb-loss updates.');
  }

  if (capHost) {
    const unique = Array.from(new Set(capabilityChips)).sort();
    capHost.innerHTML = unique
      .map(cap => `<span class="terrain-chip terrain-flat" style="margin:0 6px 6px 0">${escHtml(cap)}</span>`)
      .join('') || '<span style="color:var(--ink3)">No plugin capabilities recorded yet.</span>';
  }

  if (notesHost) {
    const lines = [
      ...notes,
      bridge?.lastSummary?.controller?.ok
        ? 'Controller bridge is responding to the core readiness probes.'
        : 'Controller bridge still looks partial; plugin signals can be used as fallback visibility.',
    ];
    notesHost.innerHTML = lines
      .map(line => `<div style="margin-bottom:6px">• ${escHtml(line)}</div>`)
      .join('');
  }

  if (readinessHost) {
    const level = summary.limbActive || summary.payloadDrag
      ? 'Attention'
      : summary.stairActive || summary.payloadAttached
        ? 'Active'
        : 'Nominal';

    const statusRows = [
      ['Stair', summary.stairActive ? `Active${summary.stairDirection ? ` · ${summary.stairDirection}` : ''}` : 'Clear'],
      ['Payload', summary.payloadText || 'Unknown'],
      ['Recovery', summary.limbActive ? `Active · ${summary.lostLimbs.join(', ')}` : summary.limbRecovery ? 'Recovered' : 'OK'],
      ['Updated', summary.updatedAt ? compactJson(summary.updatedAt, 24) : 'Waiting'],
    ];

    readinessHost.innerHTML = `
      <div style="font-weight:700;margin-bottom:6px">Plugin readiness overlay · ${escHtml(level)}</div>
      ${statusRows.map(([label, value]) => `<div style="display:flex;justify-content:space-between;gap:8px;margin-bottom:4px"><span>${escHtml(label)}</span><span>${escHtml(value)}</span></div>`).join('')}
    `;
  }

  if (commandHost && bridge) {
    const signalEvents = [
      summary.stairActive ? `stair:${summary.stairProgress || summary.stairDirection || 'active'}` : null,
      summary.payloadText ? `payload:${summary.payloadText}` : null,
      summary.limbActive ? `recovery:${summary.lostLimbs.join(',')}` : summary.limbRecovery ? 'recovery:cleared' : null,
    ].filter(Boolean);

    const rows = [
      ...signalEvents.map(item => ({ action: item, status: 'signal', endpoint: 'plugin-status' })),
      ...(bridge.commandHistory || []).slice(0, 3),
    ].slice(0, 5);

    commandHost.innerHTML = rows.length
      ? rows.map(entry => `
          <div style="padding:6px 0;border-top:1px solid rgba(255,255,255,.06)">
            <div style="font-weight:600">${escHtml(entry.action || entry.id || 'event')}</div>
            <div style="color:var(--ink3)">${escHtml(entry.status || 'unknown')} · ${escHtml(entry.endpoint || 'n/a')}</div>
          </div>
        `).join('')
      : '<div style="color:var(--ink3)">No plugin event activity yet.</div>';
  }
}

// ── Payload ───────────────────────────────────────────────────────────────────

export function applyPayload(d) {
  if (!d || typeof d !== 'object') return;
  P.payload = d;
  noteSignal('payload', d);

  // Log significant events.
  if (d.event === 'payload.drag_warning') log('warn', `⚠️ Payload drag${d.direction ? ': ' + d.direction : ''}`);
  if (d.event === 'payload.attached')     log('ok',   '📦 Payload attached');
  if (d.event === 'payload.detached')     log('info',  '📭 Payload detached');
  if (d.event === 'payload.scan_result')  log('info',  `🔬 Scan: ${JSON.stringify(d.result ?? {}).slice(0, 60)}`);

  // Badge (optional).
  // Metrics tab text cell (optional)
  const info = el('payload-info');
  if (info) {
    info.textContent = d.drag_warning  ? `⚠ Drag ${d.direction ?? ''}`
                     : (d.attached ?? (d.event === 'payload.attached')) ? 'Attached'
                     : 'Detached';
    info.className = 'tval ' + (d.drag_warning ? 'warn' : '');
  }

  const badge = el('payload-badge');
  if (badge) {
    const drag     = d.drag_warning;
    const attached = d.attached ?? (d.event === 'payload.attached');
    badge.textContent   = drag     ? '📦⚠ Drag'
                        : attached ? '📦 Attached'
                        : '📭 Detached';
    badge.className     = 'terrain-chip ' + (drag ? 'terrain-rough' : attached ? 'terrain-flat' : '');
    badge.style.display = 'inline-flex';
  }

  renderCompatibilityNotes();
}

// ── Limb loss ─────────────────────────────────────────────────────────────────

export function applyLimbLoss(d) {
  if (!d || typeof d !== 'object') return;
  P.limbLoss = d;
  noteSignal('limbLoss', d);

  const lost      = Array.isArray(d.limbs_lost) && d.limbs_lost.length > 0;
  const recovered = d.recovered || d.event === 'limb_loss.cleared';

  if (lost && !recovered)
    log('err', `🦵 Limb loss: ${d.limbs_lost.join(', ')} — recovery active`);
  if (recovered)
    log('ok', '✅ Limb recovery confirmed');

  // Metrics tab text cell (optional)
  const linfo = el('limb-info');
  if (linfo) {
    linfo.textContent = recovered ? 'Recovered' : lost ? `Lost: ${d.limbs_lost.join(', ')}` : 'OK';
    linfo.className = 'tval ' + (lost && !recovered ? 'err' : recovered ? 'ok' : '');
  }

  const badge = el('limb-loss-badge');
  if (badge) {
    badge.textContent   = recovered ? '🦵 ✅ Recovered'
                        : lost      ? `🦵 ⚠ Lost: ${d.limbs_lost.join(', ')}`
                        : '🦵 OK';
    badge.className     = 'terrain-chip ' + (lost && !recovered ? 'terrain-rough' : '');
    badge.style.display = (lost || recovered) ? 'inline-flex' : 'none';
  }

  // Highlight silhouette if canvas module exposes a hook.
  if (typeof window._highlightLimb === 'function' && Array.isArray(d.limbs_lost))
    window._highlightLimb(d.limbs_lost, recovered);

  renderCompatibilityNotes();
}

// ── Stair ─────────────────────────────────────────────────────────────────────

export function applyStair(d) {
  if (!d || typeof d !== 'object') return;
  P.stair = d;
  noteSignal('stair', d);

  if (d.event === 'stair.detected') log('warn', `⚠️ Stair: ${d.direction ?? ''} ${d.step_count ? d.step_count + ' steps' : ''}`);
  if (d.event === 'stair.exited')   log('ok',   '✅ Stair traverse complete');
  if (d.status === 'climbing')      log('info',  `🪜 Step ${d.step ?? '?'}`);

  const active = d.status === 'climbing' || d.event === 'stair.detected';

  const badge = el('stair-badge');
  if (badge) {
    badge.textContent   = active ? `🪜 Stair ${d.direction ?? ''}` : '🪜 Clear';
    badge.className     = 'terrain-chip ' + (active ? 'terrain-incline_up' : '');
    badge.style.display = active ? 'inline-flex' : 'none';
  }

  const info = el('stair-info');
  if (info) {
    info.textContent = d.event === 'stair.exited'    ? 'Clear'
      : d.status === 'climbing'                      ? `Climbing: ${d.step ?? '?'} / ${d.step_count ?? '?'}`
      : d.event === 'stair.detected'                 ? `Detected: ${d.direction ?? ''}`
      : '—';
  }

  renderCompatibilityNotes();
}
