let runtimePollHandle = null;
let runtimeSocket = null;

function wsUrlFor(path) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

function startRuntimePolling(onTick) {
  if (runtimePollHandle) {
    clearInterval(runtimePollHandle);
  }

  runtimePollHandle = setInterval(async () => {
    try {
      const state = await fetchRuntimeState();
      onTick(state);
      setConnectionState(true);
    } catch (error) {
      setConnectionState(false, error.message);
    }
  }, 2500);
}

function stopRuntimePolling() {
  if (runtimePollHandle) {
    clearInterval(runtimePollHandle);
    runtimePollHandle = null;
  }
}

function connectRuntimeSocket(onState, onEvent) {
  if (runtimeSocket && runtimeSocket.readyState === WebSocket.OPEN) {
    return;
  }

  runtimeSocket = new WebSocket(wsUrlFor("/sweetie/ws"));

  runtimeSocket.onopen = () => {
    stopRuntimePolling();
    setConnectionState(true);
  };

  runtimeSocket.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "runtime_state") {
      onState(message.data);
      return;
    }

    if (message.type === "heartbeat") {
      setConnectionState(true);
      return;
    }

    onEvent(message);
  };

  runtimeSocket.onclose = () => {
    setConnectionState(false, "WebSocket disconnected");
    startRuntimePolling(onState);
    window.setTimeout(() => connectRuntimeSocket(onState, onEvent), 2000);
  };

  runtimeSocket.onerror = () => {
    setConnectionState(false, "WebSocket error");
  };
}
