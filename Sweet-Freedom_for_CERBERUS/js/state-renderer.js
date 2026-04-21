function formatValue(value, fallback = "—") {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "number") return Number(value).toFixed(2);
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

function renderRuntimeState(state) {
  renderExpressionPanel(state);
  renderEmotionPanel(state?.emotion || {});
  renderSafetyPanel(state?.safety || {});
  renderTelemetryPanel(state?.telemetry || {});
  renderResultPanel(state?.last_action_result || {});
  renderGoalPanel(state?.active_goal || null, state?.last_feedback || null, state?.goal_result || null);
  renderSessionPanel(state?.session || null);
  renderControlSourcePanel(state?.command_mux || null);
  renderDiagnosticsPanel(state?.diagnostics || null);
  renderRecordingPanel(state?.recording || null);
  renderReplayPanel(state?.replay || null);
  renderLifecyclePanel(state?.lifecycle || null);
}
