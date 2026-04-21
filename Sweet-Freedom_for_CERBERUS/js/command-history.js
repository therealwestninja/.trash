const commandHistoryEls = {
  list: document.getElementById("command-history-list")
};

function renderCommandHistory(entries) {
  if (!commandHistoryEls.list) return;
  const items = Array.isArray(entries) ? entries : [];

  if (!items.length) {
    commandHistoryEls.list.innerHTML = '<div class="history-empty">No commands yet.</div>';
    return;
  }

  commandHistoryEls.list.innerHTML = "";

  items.forEach((entry) => {
    const row = document.createElement("article");
    row.className = "history-entry";

    const actionName =
      entry?.action?.action ||
      entry?.action?.action_type ||
      entry?.action?.type ||
      "unknown";

    const status = entry?.result?.status || "unknown";
    const motionState = entry?.motion_state || "—";
    const timestamp = entry?.timestamp
      ? new Date(entry.timestamp * 1000).toLocaleTimeString()
      : "—";

    row.innerHTML = `
      <div class="history-topline">
        <strong>${actionName}</strong>
        <span class="history-status">${status}</span>
      </div>
      <div class="history-meta">
        <span>${timestamp}</span>
        <span>${motionState}</span>
      </div>
      <div class="history-text">${entry?.text || "—"}</div>
    `;

    commandHistoryEls.list.appendChild(row);
  });
}
