const replayPanelEls = {
  panel: document.getElementById("replay-panel"),
  loadBtn: document.getElementById("replay-load-btn"),
  stepBtn: document.getElementById("replay-step-btn"),
  clearBtn: document.getElementById("replay-clear-btn"),
  input: document.getElementById("replay-jsonl-input")
};

function renderReplayPanel(replay) {
  if (!replayPanelEls.panel) return;
  const data = replay || {};

  replayPanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Loaded</strong><span>${data.is_loaded ? "Yes" : "No"}</span></div>
      <div class="row"><strong>Cursor</strong><span>${data.cursor ?? "—"}</span></div>
      <div class="row"><strong>Events</strong><span>${data.event_count ?? "—"}</span></div>
      <div class="row"><strong>Next Type</strong><span>${data.next_event?.type || "—"}</span></div>
    </article>
  `;
}

function bindReplayPanel() {
  if (replayPanelEls.loadBtn) {
    replayPanelEls.loadBtn.addEventListener("click", async () => {
      try {
        const result = await loadReplay(replayPanelEls.input?.value || "");
        renderReplayPanel(result);
        addFeedEntry("Replay loaded", result);
      } catch (error) {
        addFeedEntry("Replay load failed", error.message);
      }
    });
  }

  if (replayPanelEls.stepBtn) {
    replayPanelEls.stepBtn.addEventListener("click", async () => {
      try {
        const result = await stepReplay();
        renderReplayPanel(result.replay);
        addFeedEntry("Replay step", result.event);
      } catch (error) {
        addFeedEntry("Replay step failed", error.message);
      }
    });
  }

  if (replayPanelEls.clearBtn) {
    replayPanelEls.clearBtn.addEventListener("click", async () => {
      try {
        const result = await clearReplay();
        renderReplayPanel(result);
        addFeedEntry("Replay cleared", result);
      } catch (error) {
        addFeedEntry("Replay clear failed", error.message);
      }
    });
  }
}
