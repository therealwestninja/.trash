const expressionPanelEls = {
  mode: document.getElementById("state-mode"),
  expression: document.getElementById("state-expression"),
  animation: document.getElementById("state-animation"),
  action: document.getElementById("state-action"),
  movementStyle: document.getElementById("state-movement-style"),
  idleBehavior: document.getElementById("state-idle-behavior")
};

function renderExpressionPanel(state) {
  const expression = state?.expression || {};
  const animation = state?.animation || {};
  const presence = state?.presence || {};
  const currentAction = state?.current_action || {};

  if (expressionPanelEls.mode) {
    expressionPanelEls.mode.textContent = formatValue(state?.mode || state?.hardware_mode || "simulation");
  }

  if (expressionPanelEls.expression) {
    expressionPanelEls.expression.textContent = formatValue(expression.expression || state?.current_expression);
  }

  if (expressionPanelEls.animation) {
    expressionPanelEls.animation.textContent = formatValue(animation.current_clip || state?.current_clip);
  }

  if (expressionPanelEls.action) {
    expressionPanelEls.action.textContent = formatValue(
      currentAction.action || currentAction.action_type || currentAction.type || state?.current_action_name
    );
  }

  if (expressionPanelEls.movementStyle) {
    expressionPanelEls.movementStyle.textContent = formatValue(expression.movement_style);
  }

  if (expressionPanelEls.idleBehavior) {
    expressionPanelEls.idleBehavior.textContent = formatValue(presence.idle_behavior);
  }
}
