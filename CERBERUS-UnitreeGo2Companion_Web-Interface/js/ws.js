let socket;

function connectWS() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${proto}://${location.host}/ws`);

  socket.onopen = () => {
    setStatus("Connected");
  };

  socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleWS(msg);
  };

  socket.onclose = () => {
    setStatus("Disconnected");
    setTimeout(connectWS, 2000);
  };

  socket.onerror = () => {
    setStatus("WebSocket error");
  };
}

function sendWS(data) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  }
}
