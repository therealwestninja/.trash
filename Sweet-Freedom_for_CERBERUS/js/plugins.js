let plugins = [];

async function loadPlugins() {
  const data = await apiGet("/plugins/catalog");
  plugins = data.plugins || [];
  renderPlugins();
}

function extractParams(signature) {
  const match = signature.match(/\((.*?)\)/);
  if (!match) return [];

  return match[1]
    .split(",")
    .map(s => s.trim().split(":")[0])
    .filter(Boolean);
}

function buildForm(action) {
  const container = document.createElement("div");
  const params = extractParams(action.signature || "()");

  params.forEach(p => {
    const input = document.createElement("input");
    input.placeholder = p;
    input.id = `param-${p}`;
    container.appendChild(input);
  });

  return container;
}

function groupPlugins(plugins) {
  const groups = {
    movement: [],
    sensors: [],
    cognition: [],
    misc: []
  };

  plugins.forEach(p => {
    const caps = p.manifest?.capabilities || [];

    if (caps.includes("motion")) groups.movement.push(p);
    else if (caps.includes("sensor")) groups.sensors.push(p);
    else if (caps.includes("nlu")) groups.cognition.push(p);
    else groups.misc.push(p);
  });

  return groups;
}

function renderPluginCard(plugin) {
  const card = document.createElement("div");
  card.className = "plugin-card";

  const title = document.createElement("h3");
  title.innerText = plugin.name;
  card.appendChild(title);

  (plugin.actions || []).forEach(action => {
    const btn = document.createElement("button");
    btn.innerText = action.name;
    btn.onclick = () => openModal(plugin, action, buildForm(action));
    card.appendChild(btn);
  });

  return card;
}

function renderPlugins() {
  const container = document.getElementById("plugin-container");
  container.innerHTML = "";

  const grouped = groupPlugins(plugins);

  Object.entries(grouped).forEach(([name, list]) => {
    if (!list.length) return;
    const section = document.createElement("div");
    section.className = "plugin-section";
    section.innerHTML = `<h2>${name.toUpperCase()}</h2>`;

    list.forEach(p => section.appendChild(renderPluginCard(p)));
    container.appendChild(section);
  });
}
