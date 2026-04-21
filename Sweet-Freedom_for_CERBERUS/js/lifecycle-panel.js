const lifecyclePanelEls = {
  panel: document.getElementById("lifecycle-panel"),
  recoverBtn: document.getElementById("lifecycle-recover-btn")
};

function renderLifecyclePanel(lifecycle) {
  if (!lifecyclePanelEls.panel) return;
  const data = lifecycle || {};

  lifecyclePanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Phase</strong><span>${data.phase || "—"}</span></div>
      <div class="row"><strong>Reason</strong><span>${data.reason || "—"}</span></div>
      <div class="row"><strong>Updated</strong><span>${data.updated_at ? new Date(data.updated_at * 1000).toLocaleTimeString() : "—"}</span></div>
    </article>
  `;
}

function bindLifecyclePanel() {
  if (lifecyclePanelEls.recoverBtn) {
    lifecyclePanelEls.recoverBtn.addEventListener("click", async () => {
      try {
        const result = await recoverLifecycle();
        applyState(result);
        addFeedEntry("Lifecycle recovered", result.lifecycle || result);
      } catch (error) {
        addFeedEntry("Lifecycle recovery failed", error.message);
      }
    });
  }
}
