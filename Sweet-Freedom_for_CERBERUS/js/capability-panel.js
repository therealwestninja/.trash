const capabilityPanelEls = {
  panel: document.getElementById("capability-panel")
};

function renderCapabilityPanel(snapshot) {
  if (!capabilityPanelEls.panel) return;

  const capabilities = snapshot?.capabilities || [];
  const categories = snapshot?.categories || [];

  if (!capabilities.length) {
    capabilityPanelEls.panel.innerHTML = '<div class="session-empty">No capabilities available.</div>';
    return;
  }

  capabilityPanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Total</strong><span>${snapshot.count || capabilities.length}</span></div>
      <div class="row"><strong>Categories</strong><span>${categories.join(", ") || "—"}</span></div>
    </article>
    ${capabilities.map((cap) => `
      <article class="session-entry">
        <div class="row"><strong>${cap.title}</strong><span>${cap.enabled ? "Enabled" : "Planned"}</span></div>
        <div class="row"><span>${cap.category}</span><span>${cap.source}</span></div>
        <div class="row"><span>${cap.description}</span><span>${cap.safety_level}</span></div>
      </article>
    `).join("")}
  `;
}
