/**
 * main.js — patched module orchestrator for the CERBERUS Companion Web Interface.
 *
 * Patch_1 applied and Sweetie-Bot controller requirements integrated.
 */
import { P, loadKey, el, log, renderLogImpl } from './config.js';
import { showAuthModal, hideAuthModal, authConnect, authSkip } from './auth.js';
import { connectWS, reconnectWS, enterSimMode, sendWsCmd } from './ws.js';
import { apiCmd } from './cmd.js';
import { initInput } from './input.js';
import { initJoystick } from './joystick.js';
import { initGamepad } from './gamepad.js';
import { initKeyboard } from './keyboard.js';
import { startSimLoop, simCmd, loadBuiltinBehaviors, loadBuiltinObjects, loadBuiltinMissions } from './simulation.js';
import { drawRobot, drawBT, simulateBTStatus } from './canvas.js';
import { applyTelemetry } from './telemetry.js';
import { applyFSM } from './fsm.js';
import { applyPayload, applyLimbLoss, applyStair } from './plugin-status.js';
import { showStaleWarning, clearStaleWarning, setModeBadge, renderTerrainBadge, triggerEstop, toggleArm, cmd, bctrl, setPolicy, renderNodes, goTab, rpTab, openMin, closeMin, setTheme, btCmd, updateThresh } from './ui.js';
import { loadBehaviors, renderBehaviors, filterCat, runBeh, loadObjects, renderObjects, selObj, openAddObj, closeAddObj, submitAddObj, exportObjs, importObjs, handleObjImport, loadMissions, renderMissions, createMission, startMission, stopMission, renderPlugins, enablePlugin, disablePlugin } from './behaviors.js';
import { loadMetrics, fetchProm, renderBB, loadSafetyEvents, renderSafetyEvents } from './metrics.js';
import { initAnimation, animLoad, animPlay, animPause, animStop, animSetSpeed, animSetLoop, animSeek, animTick, loadAnimFormat, handleAnimFile, exportAnim, renderAnimClipList } from './animation.js';
import { setLocale, renderLangGrid, loadI18n } from './i18n.js';
import { genAI } from './ai.js';
import { renderFunScriptUI, fsPlay, fsPause, fsStop, fsSetSpeed, fsSetLoop, fsSetInterp, fsSmooth, fsDeleteSelected, fsExport, fsImport, fsHandleFile, fsGenerateSine, fsScrub } from './funscript.js';
import { renderDiagnosticsUI, runDiagnostics } from './diagnostics.js';
import { initSweetieIntegration } from './sweetie.js';
import { initControlProfile } from './control-profile.js';

window._applyTelemetry = applyTelemetry;
window._setSpeedIndicator = (multiplier) => {
  const fill = document.getElementById('speed-arc-fill');
  if (fill) {
    const pct = Math.min(100, (multiplier / 2.0) * 100);
    fill.style.width = pct + '%';
    fill.className = 'speed-arc-fill' + (multiplier > 1.5 ? ' sprint' : multiplier > 1.0 ? ' boost' : '');
  }
  const val = document.getElementById('speed-hud-val');
  if (val) val.textContent = '×' + multiplier.toFixed(1);
};
window._showEstopCountdown = (pct) => {
  let node = document.getElementById('estop-countdown');
  if (!node) {
    node = document.createElement('div');
    node.id = 'estop-countdown';
    node.innerHTML = '🛑 Hold combo for E-STOP… <span id="estop-pct">0%</span>';
    document.body.appendChild(node);
  }
  node.style.display = 'flex';
  document.getElementById('estop-pct')?.replaceChildren(document.createTextNode(Math.round(pct * 100) + '%'));
};
window._clearEstopCountdown = () => { const n=document.getElementById('estop-countdown'); if (n) n.style.display='none'; };
window._setModeBadge = setModeBadge;
window._applyFSM = applyFSM;
window._applyPayload = applyPayload;
window._applyLimbLoss = applyLimbLoss;
window._applyStair = applyStair;
window._showStaleWarning = showStaleWarning;
window._clearStaleWarning = clearStaleWarning;
window._renderTerrainBadge = renderTerrainBadge;
window._renderPlugins = renderPlugins;
window._simCmd = simCmd;
window._simulateBT = simulateBTStatus;
window._animTick = animTick;


function escHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function compact(value, max = 88) {
  try {
    const raw = typeof value === 'string' ? value : JSON.stringify(value);
    return raw.length > max ? `${raw.slice(0, Math.max(0, max - 1))}…` : raw;
  } catch {
    return String(value ?? '');
  }
}

function getSweetieBridgeInstance() {
  return window.SweetieBridge || null;
}

function recordControllerActivity(entry = {}) {
  const bridge = getSweetieBridgeInstance();
  if (!bridge?.addCommandHistory) return;
  bridge.addCommandHistory({
    endpoint: 'controller-ui',
    status: 'info',
    ...entry,
  });
}

function wrapWindowCommand(name, buildEntry) {
  const original = window[name];
  if (typeof original !== 'function' || original.__cerberusWrapped) return;

  const wrapped = async (...args) => {
    const bridge = getSweetieBridgeInstance();
    const descriptor = typeof buildEntry === 'function' ? buildEntry(args) : { action: name, params: args };
    const commandId = `${name}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const pending = {
      id: commandId,
      action: descriptor?.action || name,
      endpoint: descriptor?.endpoint || 'controller-ui',
      params: descriptor?.params || null,
      status: 'queued',
    };

    try {
      bridge?.setActiveCommand?.(commandId, pending);
      bridge?.addCommandHistory?.(pending);
      const result = await Promise.resolve(original(...args));
      bridge?.completeActiveCommand?.(commandId, result?.ok === false ? 'failed' : 'completed', result, result?.ok === false ? (result?.detail || result?.reason || result?.error || 'Command failed') : null);
      renderControllerActivity();
      return result;
    } catch (error) {
      bridge?.completeActiveCommand?.(commandId, 'failed', null, error?.message || String(error));
      renderControllerActivity();
      throw error;
    }
  };

  wrapped.__cerberusWrapped = true;
  wrapped.__cerberusOriginal = original;
  window[name] = wrapped;
}

function installCommandActivityWrappers() {
  if (window.__cerberusCommandWrappersInstalled) return;
  window.__cerberusCommandWrappersInstalled = true;

  wrapWindowCommand('cmd', ([action]) => ({ action, endpoint: 'controller-ui' }));
  wrapWindowCommand('bctrl', ([param, value]) => ({ action: `BODY_CTRL:${param}`, params: { [param]: value }, endpoint: 'controller-ui' }));
  wrapWindowCommand('setPolicy', ([policy]) => ({ action: 'SET_POLICY', params: { policy }, endpoint: 'controller-ui' }));
  wrapWindowCommand('runBeh', ([behaviorId]) => ({ action: 'RUN_BEHAVIOR', params: { behavior_id: behaviorId }, endpoint: 'controller-ui' }));
  wrapWindowCommand('startMission', ([missionId]) => ({ action: 'MISSION_START', params: { mission_id: missionId }, endpoint: 'controller-ui' }));
  wrapWindowCommand('stopMission', ([missionId]) => ({ action: 'MISSION_STOP', params: { mission_id: missionId }, endpoint: 'controller-ui' }));
  wrapWindowCommand('enablePlugin', ([pluginId]) => ({ action: 'PLUGIN_ENABLE', params: { plugin_id: pluginId }, endpoint: 'controller-ui' }));
  wrapWindowCommand('disablePlugin', ([pluginId]) => ({ action: 'PLUGIN_DISABLE', params: { plugin_id: pluginId }, endpoint: 'controller-ui' }));
  wrapWindowCommand('triggerEstop', () => ({ action: 'ESTOP_TOGGLE', endpoint: 'controller-ui' }));
  wrapWindowCommand('toggleArm', () => ({ action: 'ARM_TOGGLE', endpoint: 'controller-ui' }));
  wrapWindowCommand('btCmd', ([action]) => ({ action: `BT:${action}`, endpoint: 'behavior-tree' }));
}

function renderControllerActivity() {
  const bridge = getSweetieBridgeInstance();
  const commandLogEl = document.getElementById('plugins-command-log');
  const readinessEl = document.getElementById('plugins-controller-readiness');
  const pluginCountEl = document.getElementById('plugins-summary-count');
  const pluginCompatEl = document.getElementById('plugins-summary-compat');
  if (!commandLogEl && !readinessEl && !pluginCountEl && !pluginCompatEl) return;

  const summary = bridge?.lastSummary || null;
  const active = bridge?.activeCommands ? Array.from(bridge.activeCommands.values()) : [];
  const history = bridge?.commandHistory || [];
  const logFallback = (P.logs || [])
    .filter(entry => /sweetie|plugin|execute|mission|policy|estop|follow|patrol|behavior/i.test(entry.msg || ''))
    .slice(0, 4)
    .map(entry => ({
      id: `log-${entry.ts}-${entry.msg}`,
      action: entry.msg,
      endpoint: 'ui-log',
      status: entry.lvl,
      ts: entry.ts,
    }));

  const rows = [...active, ...history.slice(0, 6), ...logFallback]
    .filter((entry, idx, arr) => arr.findIndex(other => other.id === entry.id && other.action === entry.action) === idx)
    .slice(0, 8);

  if (commandLogEl) {
    commandLogEl.innerHTML = rows.length
      ? rows.map(entry => {
          const state = entry.status || (bridge?.activeCommands?.has?.(entry.id) ? 'running' : 'completed');
          const tone = /fail|err/i.test(state) ? 'err' : /queue|run|active|pending/i.test(state) ? 'warn' : 'ok';
          const detail = entry.error || entry.detail || compact(entry.params || entry.result || '', 72);
          return `<div style="padding:7px 0;border-top:1px solid rgba(255,255,255,.06)">
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:center">
              <div style="font-weight:600">${escHtml(entry.action || entry.id || 'command')}</div>
              <span class="nst ${tone}">${escHtml(state)}</span>
            </div>
            <div style="color:var(--ink3);margin-top:2px">${escHtml(entry.endpoint || 'controller-ui')} · ${escHtml(entry.ts || 'now')}</div>
            <div style="color:var(--ink3);margin-top:2px">${escHtml(detail || 'No extra details')}</div>
          </div>`;
        }).join('')
      : 'No controller/plugin orchestration events yet.';
  }

  if (readinessEl) {
    if (summary?.controller) {
      const controller = summary.controller;
      const readyText = controller.ok ? 'Controller can satisfy the core Sweetie contract right now.' : 'Controller compatibility is partial; some Sweetie surfaces still need work.';
      const lines = [
        `${readyText}`,
        `Surfaces online: ${(controller.available || []).join(', ') || 'none'}`,
        `Missing: ${(controller.missing || []).join(', ') || 'none'}`,
        `Goal: ${compact(controller.goal || '—', 48)}`,
        `Motion: ${compact(controller.stateSummary?.motion || '—', 48)}`,
      ];
      readinessEl.innerHTML = lines.map(line => `<div>${escHtml(line)}</div>`).join('');
    } else {
      readinessEl.textContent = 'Waiting for Sweetie stack probe…';
    }
  }

  if (pluginCountEl) {
    const total = summary?.totalPlugins ?? (bridge?.cfg ? Object.keys(bridge.cfg || {}).length : '—');
    const online = summary?.onlinePlugins;
    pluginCountEl.textContent = typeof online === 'number' && typeof total === 'number' ? `${online}/${total}` : String(total);
  }

  if (pluginCompatEl) {
    pluginCompatEl.textContent = summary ? `${summary.compatiblePlugins}/${summary.totalPlugins}` : 'Unknown';
    pluginCompatEl.className = 'tval ' + ((summary?.compatiblePlugins || 0) > 0 ? 'ok' : 'warn');
  }
}

function startControllerActivityMonitor() {
  if (window.__cerberusActivityMonitorStarted) return;
  window.__cerberusActivityMonitorStarted = true;
  renderControllerActivity();
  setInterval(renderControllerActivity, 1500);
}


Object.assign(window, {
  authConnect, authSkip, showAuthModal, hideAuthModal,
  connectWS, enterSimMode, reconnect: reconnectWS, sendWsCmd,
  goTab, rpTab, openMin, closeMin,
  cmd, bctrl, setPolicy, triggerEstop, toggleArm,
  runBeh, filterCat, renderBehaviors, renderObjects, renderMissions,
  selObj, openAddObj, closeAddObj, submitAddObj, exportObjs, importObjs, handleObjImport,
  createMission, startMission, stopMission, enablePlugin, disablePlugin, renderPlugins,
  animLoad, animPlay, animPause, animStop, animSetSpeed, animSetLoop, animSeek, loadAnimFormat, handleAnimFile, exportAnim, renderAnimClipList,
  loadMetrics, fetchProm, btCmd, renderBB, loadSafetyEvents, renderSafetyEvents,
  setLocale, renderLangGrid, updateThresh, setTheme,
  genAI,
  renderFunScriptUI, fsPlay, fsPause, fsStop, fsSetSpeed, fsSetLoop, fsSetInterp, fsSmooth, fsDeleteSelected, fsExport, fsImport, fsHandleFile, fsGenerateSine, fsScrub,
  renderDiagnosticsUI, runDiagnostics,
});

document.addEventListener('DOMContentLoaded', async () => {
  log('ok', 'CERBERUS Companion UI — Patch_1 + Sweetie integration initializing');
  loadBuiltinBehaviors();
  loadBuiltinObjects();
  loadBuiltinMissions();

  const controlProfile = initControlProfile();

  initAnimation();
  initInput();
  initJoystick();
  initGamepad();
  initKeyboard();
  initSweetieIntegration();
  installCommandActivityWrappers();
  startControllerActivityMonitor();
  recordControllerActivity({ action: 'UI_INIT', status: 'completed', detail: 'Companion UI boot sequence started' });

  await loadI18n?.(P.locale);
  renderBehaviors();
  renderObjects();
  renderMissions();
  renderLangGrid();
  renderNodes();
  renderBB();
  renderFunScriptUI();
  renderDiagnosticsUI();
  drawRobot(P.telemetry);
  drawBT();
  renderAnimClipList();

  document.querySelector('[data-action="clear-log"]')?.addEventListener('click', () => { P.logs = []; renderLogImpl(); });
  startSimLoop();
  setInterval(renderNodes, 2000);
  setInterval(() => { if (el('tab-metrics')?.classList.contains('active')) loadMetrics(); }, 5000);

  const urlEl = el('api-url');
  if (urlEl) { urlEl.value = P.apiBase; urlEl.addEventListener('change', () => { P.apiBase = urlEl.value.trim(); }); }
  el('sim-chk')?.addEventListener('change', e => { P.simMode = e.target.checked; if (P.simMode) enterSimMode(); });
  el('debug-chk')?.addEventListener('change', e => { P.debug = e.target.checked; });

  const key = loadKey();
  if (controlProfile?.preferSim) {
    enterSimMode();
    recordControllerActivity({ action: 'PROFILE_SIM_READY', status: 'completed', detail: controlProfile.label });
  } else if (key) {
    log('info', 'Key found — connecting to ' + P.apiBase);
    connectWS();
    recordControllerActivity({ action: 'WS_CONNECT', status: 'queued', detail: P.apiBase });
  } else {
    showAuthModal();
    recordControllerActivity({ action: 'AUTH_REQUIRED', status: 'warn', detail: 'Waiting for operator key' });
  }
  log('ok', 'Init complete');
});
