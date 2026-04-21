let plugins = [];

async function loadPlugins() {
  const data = await apiGet("/plugins/catalog");
  plugins = data.plugins || [];
  renderPlugins();
}

function renderPlugins() {
  const container = document.getElementById("plugin-container");
  container.innerHTML = "";

  plugins.forEach(plugin => {
    const card = document.createElement("div");
    card.className = "plugin-card";

    const title = document.createElement("h3");
    title.innerText = plugin.manifest?.name || plugin.name;
    card.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "plugin-meta";
    meta.innerText = `${plugin.enabled ? "Enabled" : "Disabled"} · ${plugin.class_name || "Plugin"}`;
    card.appendChild(meta);

    const desc = document.createElement("p");
    desc.innerText = plugin.manifest?.description || "No description provided.";
    card.appendChild(desc);

    const actionsWrap = document.createElement("div");
    actionsWrap.className = "plugin-actions";

    (plugin.actions || []).forEach(action => {
      const btn = document.createElement("button");
      btn.innerText = action.name;
      btn.onclick = () => openModal(plugin, action);
      actionsWrap.appendChild(btn);
    });

    card.appendChild(actionsWrap);
    container.appendChild(card);
  });
}
