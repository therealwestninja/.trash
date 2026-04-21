const quickActionsUi = {
  buttons: () => document.querySelectorAll("[data-quick-action]")
};

function bindQuickActions(onQuickAction) {
  quickActionsUi.buttons().forEach((button) => {
    button.addEventListener("click", () => onQuickAction(button.dataset.quickAction));
  });
}
