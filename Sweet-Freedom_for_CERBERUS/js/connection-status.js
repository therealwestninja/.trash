const connectionStatusEls = {
  pill: document.getElementById("connection-pill")
};

function setConnectionState(connected, detail = "") {
  if (!connectionStatusEls.pill) return;

  connectionStatusEls.pill.textContent = connected ? "Connected" : "Disconnected";
  connectionStatusEls.pill.classList.toggle("ok", connected);
  connectionStatusEls.pill.classList.toggle("bad", !connected);

  if (!connected && detail) {
    connectionStatusEls.pill.title = detail;
  } else {
    connectionStatusEls.pill.removeAttribute("title");
  }
}
