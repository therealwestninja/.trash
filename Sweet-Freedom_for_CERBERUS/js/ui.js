function applyState(state) {
  renderRuntimeState(state);
  renderCommandHistory(state?.command_history || []);
}

async function refreshState() {
  try {
    const state = await fetchRuntimeState();
    applyState(state);
    setConnectionState(true);
  } catch (error) {
    setConnectionState(false, error.message);
    addFeedEntry("State refresh failed", error.message);
  }
}

async function onQuickAction(actionName) {
  try {
    const result = await sendQuickAction(actionName);
    applyState(result);
    addFeedEntry(`Quick action: ${actionName}`, result);
    setConnectionState(true);
  } catch (error) {
    addFeedEntry(`Quick action failed: ${actionName}`, error.message);
    setConnectionState(false, error.message);
  }
}

function bindUi() {
  bindOperatorConsole({
    onRefresh: refreshState,
    onStateApplied: applyState
  });
  bindQuickActions(onQuickAction);
  bindSafetyPanelControls(refreshState);
}
