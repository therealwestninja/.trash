const resultPanelEls = {
  status: document.getElementById("result-status"),
  action: document.getElementById("result-action"),
  message: document.getElementById("result-message")
};

function renderResultPanel(result) {
  const data = result || {};

  if (resultPanelEls.status) {
    resultPanelEls.status.textContent = formatValue(data.status);
  }

  if (resultPanelEls.action) {
    resultPanelEls.action.textContent = formatValue(
      data.action || data.action_type || data.type
    );
  }

  if (resultPanelEls.message) {
    resultPanelEls.message.textContent = formatValue(
      data.reason || data.message
    );
  }
}
