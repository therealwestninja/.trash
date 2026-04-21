const operatorConsoleEls = {
  form: document.getElementById("operator-form"),
  text: document.getElementById("operator-text"),
  sendBtn: document.getElementById("send-btn"),
  refreshBtn: document.getElementById("refresh-btn"),
  estopBtn: document.getElementById("estop-btn"),
  clearEstopBtn: document.getElementById("clear-estop-btn"),
  sessionAcquireBtn: document.getElementById("session-acquire-btn"),
  sessionReleaseBtn: document.getElementById("session-release-btn")
};

async function submitOperatorText(onStateApplied) {
  const text = operatorConsoleEls.text.value.trim();
  if (!text) return;

  operatorConsoleEls.sendBtn.disabled = true;
  try {
    const result = await sendOperatorText(text);
    onStateApplied(result);
    addFeedEntry("Operator text sent", result);
    operatorConsoleEls.text.value = "";
    setConnectionState(true);
  } catch (error) {
    addFeedEntry("Operator text failed", error.message);
    setConnectionState(false, error.message);
  } finally {
    operatorConsoleEls.sendBtn.disabled = false;
  }
}

async function triggerEmergencyStop(onRefresh) {
  operatorConsoleEls.estopBtn.disabled = true;
  try {
    const result = await triggerEstop();
    addFeedEntry("E-Stop triggered", result);
    await onRefresh();
  } catch (error) {
    addFeedEntry("E-Stop failed", error.message);
  } finally {
    operatorConsoleEls.estopBtn.disabled = false;
  }
}

async function clearEmergencyStop(onRefresh) {
  operatorConsoleEls.clearEstopBtn.disabled = true;
  try {
    const result = await clearEstop();
    addFeedEntry("E-Stop cleared", result);
    await onRefresh();
  } catch (error) {
    addFeedEntry("Clear E-Stop failed", error.message);
  } finally {
    operatorConsoleEls.clearEstopBtn.disabled = false;
  }
}

async function acquireOperatorSession(onRefresh) {
  operatorConsoleEls.sessionAcquireBtn.disabled = true;
  try {
    const result = await acquireSession("ui");
    addFeedEntry("Session acquired", result);
    startSessionKeepalive();
    await onRefresh();
  } catch (error) {
    addFeedEntry("Session acquire failed", error.message);
  } finally {
    operatorConsoleEls.sessionAcquireBtn.disabled = false;
  }
}

async function releaseOperatorSession(onRefresh) {
  operatorConsoleEls.sessionReleaseBtn.disabled = true;
  try {
    if (!sweetFreedomLeaseId) {
      addFeedEntry("Session release skipped", "No active lease.");
      return;
    }
    const result = await releaseSession(sweetFreedomLeaseId);
    addFeedEntry("Session released", result);
    stopSessionKeepalive();
    await onRefresh();
  } catch (error) {
    addFeedEntry("Session release failed", error.message);
  } finally {
    operatorConsoleEls.sessionReleaseBtn.disabled = false;
  }
}

function bindOperatorConsole({ onRefresh, onStateApplied }) {
  operatorConsoleEls.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitOperatorText(onStateApplied);
  });

  operatorConsoleEls.refreshBtn.addEventListener("click", onRefresh);
  operatorConsoleEls.estopBtn.addEventListener("click", async () => {
    await triggerEmergencyStop(onRefresh);
  });
  operatorConsoleEls.clearEstopBtn.addEventListener("click", async () => {
    await clearEmergencyStop(onRefresh);
  });
  operatorConsoleEls.sessionAcquireBtn.addEventListener("click", async () => {
    await acquireOperatorSession(onRefresh);
  });
  operatorConsoleEls.sessionReleaseBtn.addEventListener("click", async () => {
    await releaseOperatorSession(onRefresh);
  });
}
