const goalPanelEls = {
  panel: document.getElementById("goal-panel")
};

function renderGoalPanel(goal, feedback, result) {
  if (!goalPanelEls.panel) return;

  if (!goal) {
    goalPanelEls.panel.innerHTML = '<div class="goal-empty">No active goal.</div>';
    return;
  }

  const progress = Math.max(0, Math.min(100, Math.round((feedback?.progress || 0) * 100)));
  goalPanelEls.panel.innerHTML = `
    <article class="goal-entry">
      <div class="row"><strong>Goal ID</strong><span>${goal.goal_id || "—"}</span></div>
      <div class="row"><strong>Action</strong><span>${goal.action_type || "—"}</span></div>
      <div class="row"><strong>Status</strong><span>${feedback?.status || result?.status || "—"}</span></div>
      <div class="row"><strong>Phase</strong><span>${feedback?.phase || "—"}</span></div>
      <div class="row"><strong>Message</strong><span>${feedback?.message || result?.message || "—"}</span></div>
      <div class="goal-progress"><span style="width:${progress}%"></span></div>
      <div class="button-row">
        <button type="button" id="cancel-goal-btn" class="secondary">Cancel Goal</button>
      </div>
    </article>
  `;

  const cancelBtn = document.getElementById("cancel-goal-btn");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", async () => {
      try {
        const state = await cancelGoal(goal.goal_id);
        applyState(state);
        addFeedEntry("Goal canceled", state.goal_result || state);
      } catch (error) {
        addFeedEntry("Goal cancel failed", error.message);
      }
    });
  }
}
