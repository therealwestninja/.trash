async function initializeSweetFreedomApp() {
  bindUi();
  bindRecordingPanel();
  bindReplayPanel();
  bindLifecyclePanel();
  try {
    await refreshState();
    const replay = await fetchReplayState();
    renderReplayPanel(replay);
    const capabilities = await fetchCapabilities();
    renderCapabilityPanel(capabilities);
  } catch (error) {
    addFeedEntry("Initial load failed", error?.message || String(error));
    setConnectionState(false, error?.message || "Initial load failed");
  } finally {
    connectRuntimeSocket(
      applyState,
      (message) => handleRuntimeEvent(message, applyState)
    );
    startSessionKeepalive();
  }
}

window.addEventListener("load", initializeSweetFreedomApp);
