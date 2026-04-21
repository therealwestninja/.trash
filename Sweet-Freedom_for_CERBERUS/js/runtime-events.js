function handleRuntimeEvent(message, applyState) {
  if (message.type === "runtime_state") {
    applyState(message.data);
    return;
  }

  if (message.type === "lifecycle") {
    renderLifecyclePanel(message.data);
    addFeedEntry("Lifecycle update", message.data);
    return;
  }

  if (message.type === "replay_state") {
    renderReplayPanel(message.data);
    addFeedEntry("Replay state", message.data);
    return;
  }

  if (message.type === "replay_event") {
    addFeedEntry("Replay event", message.data);
    return;
  }

  if (message.type === "diagnostics") {
    renderDiagnosticsPanel(message.data);
    addFeedEntry("Diagnostics update", message.data);
    return;
  }

  if (message.type === "control_source") {
    renderControlSourcePanel(message.data);
    addFeedEntry("Control source update", message.data);
    return;
  }

  if (message.type === "goal_canceled") {
    addFeedEntry("Goal canceled", message.data);
    return;
  }

  if (message.type === "session_state") {
    renderSessionPanel(message.data);
    addFeedEntry("Session state", message.data);
    return;
  }

  if (message.type === "safety_event") {
    addFeedEntry("Safety event", message.data);
    return;
  }

  if (message.type === "operator_result") {
    addFeedEntry("Operator result", message.data);
    return;
  }

  if (message.type === "quick_action") {
    addFeedEntry("Quick action", message.data);
    return;
  }

  if (message.type === "presence_update") {
    addFeedEntry("Presence update", message.data);
    if (message.data?.state) {
      applyState(message.data.state);
    }
    return;
  }

  if (message.type === "heartbeat") {
    setConnectionState(true);
    return;
  }

  addFeedEntry(message.type || "Realtime event", message.data || message);
}
