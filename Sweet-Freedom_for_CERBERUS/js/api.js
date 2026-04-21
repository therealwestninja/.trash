const API = {
  runtimeState: "/sweetie/runtime_full_state",
  diagnostics: "/sweetie/diagnostics",
  capabilities: "/sweetie/capabilities",
  exportRecording: "/sweetie/recording/export",
  clearRecording: "/sweetie/recording/clear",
  replayLoad: "/sweetie/replay/load",
  replayStep: "/sweetie/replay/step",
  replayState: "/sweetie/replay/state",
  replayClear: "/sweetie/replay/clear",
  lifecycleRecover: "/sweetie/lifecycle/recover",
  operatorText: "/sweetie/operator_text",
  quickAction: "/sweetie/action/quick",
  cancelAction: "/sweetie/action/cancel",
  lockControl: "/sweetie/control/lock",
  unlockControl: "/sweetie/control/unlock",
  armSystem: "/sweetie/safety/arm",
  disarmSystem: "/sweetie/safety/disarm",
  estop: "/sweetie/safety/estop",
  clearEstop: "/sweetie/safety/clear_estop",
  acquireSession: "/sweetie/session/acquire",
  sessionCheckin: "/sweetie/session/checkin",
  releaseSession: "/sweetie/session/release",
  sessionState: "/sweetie/session/state"
};

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const text = await response.text();
  let payload = {};
  try {
    payload = text ? JSON.parse(text) : {};
  } catch (err) {
    payload = { raw: text };
  }

  if (!response.ok) {
    const message = payload?.detail || payload?.message || response.statusText;
    throw new Error(message);
  }

  return payload;
}

async function fetchRuntimeState() { return requestJson(API.runtimeState); }
async function fetchDiagnostics() { return requestJson(API.diagnostics); }
async function fetchCapabilities() { return requestJson(API.capabilities); }
async function exportRecording() { const response = await fetch(API.exportRecording); if (!response.ok) throw new Error(response.statusText); return response.text(); }
async function clearRecording() { return requestJson(API.clearRecording, { method: "POST", body: JSON.stringify({}) }); }
async function loadReplay(jsonl) { return requestJson(API.replayLoad, { method: "POST", body: JSON.stringify({ jsonl }) }); }
async function stepReplay() { return requestJson(API.replayStep, { method: "POST", body: JSON.stringify({}) }); }
async function fetchReplayState() { return requestJson(API.replayState); }
async function clearReplay() { return requestJson(API.replayClear, { method: "POST", body: JSON.stringify({}) }); }
async function recoverLifecycle() { return requestJson(API.lifecycleRecover, { method: "POST", body: JSON.stringify({}) }); }

async function sendOperatorText(text) { return requestJson(API.operatorText, { method: "POST", body: JSON.stringify({ text }) }); }
async function sendQuickAction(action) { return requestJson(API.quickAction, { method: "POST", body: JSON.stringify({ action }) }); }
async function cancelGoal(goalId) { return requestJson(API.cancelAction, { method: "POST", body: JSON.stringify({ goal_id: goalId, requested_by: "ui" }) }); }
async function lockControlSource(source) { return requestJson(API.lockControl, { method: "POST", body: JSON.stringify({ source }) }); }
async function unlockControlSource(source) { return requestJson(API.unlockControl, { method: "POST", body: JSON.stringify({ source }) }); }
async function armSystem() { return requestJson(API.armSystem, { method: "POST", body: JSON.stringify({}) }); }
async function disarmSystem() { return requestJson(API.disarmSystem, { method: "POST", body: JSON.stringify({}) }); }
async function triggerEstop() { return requestJson(API.estop, { method: "POST", body: JSON.stringify({}) }); }
async function clearEstop() { return requestJson(API.clearEstop, { method: "POST", body: JSON.stringify({}) }); }
async function acquireSession(owner = "ui") { return requestJson(API.acquireSession, { method: "POST", body: JSON.stringify({ owner }) }); }
async function sessionCheckin(leaseId) { return requestJson(API.sessionCheckin, { method: "POST", body: JSON.stringify({ lease_id: leaseId }) }); }
async function releaseSession(leaseId) { return requestJson(API.releaseSession, { method: "POST", body: JSON.stringify({ lease_id: leaseId }) }); }
async function fetchSessionState() { return requestJson(API.sessionState); }
