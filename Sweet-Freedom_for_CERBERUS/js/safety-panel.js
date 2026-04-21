const safetyPanelEls = {
  message: document.getElementById("safety-message"),
  estop: document.getElementById("safety-estop"),
  allowed: document.getElementById("safety-allowed"),
  reason: document.getElementById("safety-reason"),
  armed: document.getElementById("safety-armed"),
  armBtn: document.getElementById("arm-btn"),
  disarmBtn: document.getElementById("disarm-btn")
};

function renderSafetyPanel(safety) {
  const data = safety || {};
  const blockedReasons = Array.isArray(data.blocked_reasons) ? data.blocked_reasons : [];
  const reasonText = data.reason || blockedReasons.join(", ");

  if (safetyPanelEls.estop) {
    safetyPanelEls.estop.textContent = formatValue(data.estop_active);
  }

  if (safetyPanelEls.armed) {
    safetyPanelEls.armed.textContent = formatValue(data.armed);
  }

  if (safetyPanelEls.allowed) {
    safetyPanelEls.allowed.textContent = formatValue(
      typeof data.allowed === "boolean" ? data.allowed : data.is_allowed
    );
  }

  if (safetyPanelEls.reason) {
    safetyPanelEls.reason.textContent = formatValue(reasonText);
  }

  if (safetyPanelEls.message) {
    safetyPanelEls.message.textContent = reasonText ? formatValue(reasonText) : "No safety events yet.";
  }
}

function bindSafetyPanelControls(onRefresh) {
  if (safetyPanelEls.armBtn) {
    safetyPanelEls.armBtn.addEventListener("click", async () => {
      try {
        const result = await armSystem();
        applyState(result);
        addFeedEntry("System armed", result.safety || result);
      } catch (error) {
        addFeedEntry("Arm failed", error.message);
      }
    });
  }

  if (safetyPanelEls.disarmBtn) {
    safetyPanelEls.disarmBtn.addEventListener("click", async () => {
      try {
        const result = await disarmSystem();
        applyState(result);
        addFeedEntry("System disarmed", result.safety || result);
      } catch (error) {
        addFeedEntry("Disarm failed", error.message);
      }
    });
  }
}
