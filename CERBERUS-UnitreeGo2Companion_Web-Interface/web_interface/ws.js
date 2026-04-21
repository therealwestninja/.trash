
// ws.js - Rebuilt WebSocket integration with SweetieBridge

(function () {
  const WS_URL = (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws";

  let socket = null;

  function log(msg) {
    console.log("[WS]", msg);
  }

  function safeParse(data) {
    try { return JSON.parse(data); } catch { return null; }
  }

  function handleMessage(msg) {
    if (!msg || typeof msg !== "object") return;

    const bridge = window.SweetieBridge;
    if (!bridge) return;

    switch (msg.type) {
      case "state.update":
        bridge.state = bridge.state || {};
        bridge.state.controller = msg.payload;
        bridge.state.lastUpdated = Date.now();
        break;

      case "plugin.update":
        bridge.state = bridge.state || {};
        bridge.state.plugins = bridge.state.plugins || {};
        bridge.state.plugins[msg.plugin || "unknown"] = msg.payload;
        break;

      case "command.started":
      case "command.running":
      case "command.completed":
      case "command.failed":
      case "command.cancelled":
        if (bridge.activeCommands && msg.id) {
          bridge.activeCommands.set(msg.id, msg);
        }
        if (bridge.commandHistory) {
          bridge.commandHistory.push(msg);
        }
        break;

      case "log":
        log(msg.payload);
        break;

      default:
        log("Unhandled message: " + msg.type);
    }
  }

  function connect() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      log("Connected");
    };

    socket.onmessage = (event) => {
      const msg = safeParse(event.data);
      handleMessage(msg);
    };

    socket.onclose = () => {
      log("Disconnected. Reconnecting...");
      setTimeout(connect, 2000);
    };

    socket.onerror = (err) => {
      log("Error: " + err.message);
    };
  }

  connect();
})();
