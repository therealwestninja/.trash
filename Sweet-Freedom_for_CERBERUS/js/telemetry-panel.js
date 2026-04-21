const telemetryPanelEls = {
  motionState: document.getElementById("telemetry-motion-state"),
  commandCount: document.getElementById("telemetry-command-count"),
  lastCommandAt: document.getElementById("telemetry-last-command-at")
};

function formatTimestamp(value) {
  if (!value) return "—";
  return new Date(value * 1000).toLocaleTimeString();
}

function renderTelemetryPanel(telemetry) {
  const data = telemetry || {};

  if (telemetryPanelEls.motionState) {
    telemetryPanelEls.motionState.textContent = formatValue(data.motion_state);
  }

  if (telemetryPanelEls.commandCount) {
    telemetryPanelEls.commandCount.textContent = formatValue(data.command_count);
  }

  if (telemetryPanelEls.lastCommandAt) {
    telemetryPanelEls.lastCommandAt.textContent = formatTimestamp(data.last_command_at);
  }
}
