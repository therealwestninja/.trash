const sessionPanelEls = {
  panel: document.getElementById("session-panel"),
  message: document.getElementById("session-message")
};

let sweetFreedomLeaseId = null;
let sweetFreedomKeepaliveHandle = null;

function renderSessionPanel(sessionState) {
  const data = sessionState || {};
  const lease = data.lease || null;

  if (!sessionPanelEls.panel) return;

  if (!data.active || !lease) {
    sessionPanelEls.panel.innerHTML = '<div class="session-empty">No active session.</div>';
    if (sessionPanelEls.message) {
      sessionPanelEls.message.textContent = "No active session.";
    }
    sweetFreedomLeaseId = null;
    return;
  }

  sweetFreedomLeaseId = lease.lease_id || null;
  const expiryText = lease.expires_at ? new Date(lease.expires_at * 1000).toLocaleTimeString() : "—";

  sessionPanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Lease ID</strong><span>${lease.lease_id || "—"}</span></div>
      <div class="row"><strong>Owner</strong><span>${lease.owner || "—"}</span></div>
      <div class="row"><strong>Stale</strong><span>${lease.stale ? "Yes" : "No"}</span></div>
      <div class="row"><strong>Degraded</strong><span>${data.degraded ? "Yes" : "No"}</span></div>
      <div class="row"><strong>Expires</strong><span>${expiryText}</span></div>
    </article>
  `;

  if (sessionPanelEls.message) {
    sessionPanelEls.message.textContent = data.degraded
      ? "Session is stale. Comms-loss policy is active."
      : lease.stale
        ? "Session is stale."
        : `Active lease owned by ${lease.owner || "unknown"}.`;
  }
}

function startSessionKeepalive() {
  stopSessionKeepalive();
  sweetFreedomKeepaliveHandle = window.setInterval(async () => {
    if (!sweetFreedomLeaseId) return;
    try {
      await sessionCheckin(sweetFreedomLeaseId);
    } catch (error) {
      addFeedEntry("Session keepalive failed", error.message);
      setConnectionState(false, error.message);
    }
  }, 5000);
}

function stopSessionKeepalive() {
  if (sweetFreedomKeepaliveHandle) {
    window.clearInterval(sweetFreedomKeepaliveHandle);
    sweetFreedomKeepaliveHandle = null;
  }
}
