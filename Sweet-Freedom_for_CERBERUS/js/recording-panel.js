const recordingPanelEls = {
  panel: document.getElementById("recording-panel"),
  exportBtn: document.getElementById("recording-export-btn"),
  clearBtn: document.getElementById("recording-clear-btn")
};

function renderRecordingPanel(recording) {
  if (!recordingPanelEls.panel) return;
  const data = recording || {};

  recordingPanelEls.panel.innerHTML = `
    <article class="session-entry">
      <div class="row"><strong>Recording</strong><span>${data.is_recording ? "On" : "Off"}</span></div>
      <div class="row"><strong>Events</strong><span>${data.event_count ?? "—"}</span></div>
      <div class="row"><strong>Latest</strong><span>${data.latest_event?.type || "—"}</span></div>
    </article>
  `;
}

function bindRecordingPanel() {
  if (recordingPanelEls.exportBtn) {
    recordingPanelEls.exportBtn.addEventListener("click", async () => {
      try {
        const text = await exportRecording();
        const blob = new Blob([text], { type: "application/x-ndjson" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "sweetie-session.jsonl";
        a.click();
        URL.revokeObjectURL(url);
        addFeedEntry("Recording exported", "Downloaded session JSONL.");
      } catch (error) {
        addFeedEntry("Export failed", error.message);
      }
    });
  }

  if (recordingPanelEls.clearBtn) {
    recordingPanelEls.clearBtn.addEventListener("click", async () => {
      try {
        const result = await clearRecording();
        renderRecordingPanel(result.recording);
        addFeedEntry("Recording cleared", result);
      } catch (error) {
        addFeedEntry("Recording clear failed", error.message);
      }
    });
  }
}
