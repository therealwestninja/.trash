
import { sendNudge } from "./api.js";
import { connectWS } from "./ws.js";

function renderReaction(r) {
  console.log("Reaction:", r);
}

function renderExecution(r) {
  console.log("Execution:", r);
}

connectWS((event) => {
  switch (event.type) {
    case "events.snapshot":
      console.log("Snapshot:", event.payload);
      break;
    case "character.nudge_reaction":
      renderReaction(event.payload.reaction);
      break;
    case "cerberus.execution_ack":
      renderExecution(event.payload);
      break;
  }
});

window.sendNudge = sendNudge;
