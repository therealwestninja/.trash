const controlSourceEls = {
  panel: document.getElementById("control-source-panel")
};

function renderControlSourcePanel(commandMux) {
  if (!controlSourceEls.panel) return;

  const data = commandMux || {};
  const active = data.active_source || "—";
  const sources = data.sources || {};

  const entries = Object.values(sources);
  if (!entries.length) {
    controlSourceEls.panel.innerHTML = '<div class="session-empty">No control sources.</div>';
    return;
  }

  controlSourceEls.panel.innerHTML = `
    <div class="session-entry">
      <div class="row"><strong>Active Source</strong><span>${active}</span></div>
    </div>
    ${entries.map((source) => `
      <article class="session-entry">
        <div class="row"><strong>${source.name}</strong><span>priority ${source.priority}</span></div>
        <div class="row"><span>Locked</span><span>${source.locked ? "Yes" : "No"}</span></div>
        <div class="button-row">
          <button type="button" data-lock-source="${source.name}" class="secondary">Lock</button>
          <button type="button" data-unlock-source="${source.name}">Unlock</button>
        </div>
      </article>
    `).join("")}
  `;

  controlSourceEls.panel.querySelectorAll("[data-lock-source]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const result = await lockControlSource(btn.dataset.lockSource);
        renderControlSourcePanel(result);
        addFeedEntry("Control source locked", result);
      } catch (error) {
        addFeedEntry("Lock failed", error.message);
      }
    });
  });

  controlSourceEls.panel.querySelectorAll("[data-unlock-source]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        const result = await unlockControlSource(btn.dataset.unlockSource);
        renderControlSourcePanel(result);
        addFeedEntry("Control source unlocked", result);
      } catch (error) {
        addFeedEntry("Unlock failed", error.message);
      }
    });
  });
}
