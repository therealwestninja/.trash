const emotionPanelEls = {
  valence: document.getElementById("emotion-valence"),
  stress: document.getElementById("emotion-stress"),
  curiosity: document.getElementById("emotion-curiosity")
};

function renderEmotionPanel(emotion) {
  const data = emotion || {};

  if (emotionPanelEls.valence) {
    emotionPanelEls.valence.textContent = formatValue(data.valence);
  }

  if (emotionPanelEls.stress) {
    emotionPanelEls.stress.textContent = formatValue(data.stress);
  }

  if (emotionPanelEls.curiosity) {
    emotionPanelEls.curiosity.textContent = formatValue(data.curiosity);
  }
}
