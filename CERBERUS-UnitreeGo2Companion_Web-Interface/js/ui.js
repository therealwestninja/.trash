let currentPlugin = null;
let currentAction = null;

function setStatus(text) {
  document.getElementById("status-bar").innerText = text;
}

function handleWS(msg) {
  if (msg.type === "plugin_status" || msg.type === "plugin_execute_result" || msg.type === "error") {
    logActivity(msg.data || msg);
  }
  if (msg.type === "plugin_catalog") {
    plugins = msg.data?.plugins || [];
    renderPlugins();
  }
}

function logActivity(data) {
  const feed = document.getElementById("activity-feed");
  const entry = document.createElement("div");
  entry.className = "activity-entry";
  entry.innerText = JSON.stringify(data, null, 2);
  feed.prepend(entry);
}

function openModal(plugin, action) {
  currentPlugin = plugin;
  currentAction = action;

  document.getElementById("modal-title").innerText = `${plugin.manifest?.name || plugin.name} → ${action.name}`;
  document.getElementById("modal-form").innerHTML = `
    <label for="params">Parameters (JSON)</label>
    <textarea id="params" placeholder='{"key": "value"}'></textarea>
  `;
  document.getElementById("modal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modal").classList.add("hidden");
}

async function submitAction() {
  let params = {};
  try {
    params = JSON.parse(document.getElementById("params").value || "{}");
  } catch (err) {
    logActivity({ ok: false, error: { message: "Invalid JSON parameters" } });
    return;
  }

  try {
    const result = await apiPost(`/plugins/${currentPlugin.name}/execute`, {
      action: currentAction.name,
      params
    });
    logActivity(result);
  } catch (err) {
    logActivity({ ok: false, error: { message: err.message } });
  }
  closeModal();
}

window.onload = async () => {
  connectWS();
  try {
    await loadPlugins();
  } catch (err) {
    logActivity({ ok: false, error: { message: err.message } });
  }
};
