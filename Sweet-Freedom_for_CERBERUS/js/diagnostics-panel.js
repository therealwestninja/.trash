const diagnosticsPanelEls = {
  panel: document.getElementById("diagnostics-panel")
};

function renderDiagnosticsPanel(diagnostics) {
  if (!diagnosticsPanelEls.panel) return;
  const summary = diagnostics?.summary || {};

  diagnosticsPanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Motion</strong><span>${summary.motion_state || "—"}</span></div>
      <div class="row"><strong>Armed</strong><span>${summary.armed ? "Yes" : "No"}</span></div>
      <div class="row"><strong>E-Stop</strong><span>${summary.estop_active ? "Yes" : "No"}</span></div>
      <div class="row"><strong>Source</strong><span>${summary.active_source || "—"}</span></div>
      <div class="row"><strong>Session</strong><span>${summary.session_active ? "Active" : "Inactive"}</span></div>
      <div class="row"><strong>Degraded</strong><span>${summary.degraded ? "Yes" : (summary.session_degraded ? "Yes" : "No")}</span></div>
      <div class="row"><strong>Goal</strong><span>${summary.active_goal || "—"}</span></div>
      <div class="row"><strong>Goal Status</strong><span>${summary.goal_status || "—"}</span></div>
    </article>
  `;
}
