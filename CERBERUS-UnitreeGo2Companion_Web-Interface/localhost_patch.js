import { initSweetieIntegration } from './sweetie.js';

function updateDeviceIndicator(label) {
  const el = document.getElementById('input-device-indicator');
  if (el) el.textContent = label || '— none';
}

function initInputPatch() {
  updateDeviceIndicator('keyboard / local');
  window.addEventListener('gamepadconnected', (e) => {
    const name = e?.gamepad?.id ? `gamepad: ${e.gamepad.id}` : 'gamepad';
    updateDeviceIndicator(name);
  });
  window.addEventListener('gamepaddisconnected', () => updateDeviceIndicator('keyboard / local'));

  const resetBtn = document.getElementById('input-reset-bindings');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      localStorage.removeItem('cerberus_input_bindings_v1');
      updateDeviceIndicator('keyboard / local');
      alert('Input bindings reset. Reload LocalHost.html to reinitialize defaults.');
    });
  }

  const bindingsList = document.getElementById('input-bindings-list');
  if (bindingsList) {
    const defaults = [
      ['forward', 'W / ArrowUp'],
      ['back', 'S / ArrowDown'],
      ['left', 'A / ArrowLeft'],
      ['right', 'D / ArrowRight'],
      ['turn_left', 'Q'],
      ['turn_right', 'E'],
      ['estop', 'Space'],
    ];
    bindingsList.innerHTML = defaults.map(([name, val]) => `
      <div class="node-row" style="align-items:center;gap:8px">
        <span class="node-name" style="flex:1">${name}</span>
        <span style="font-family:var(--mono);font-size:11px;color:var(--ink2)">${val}</span>
        <button class="btn btn-ghost" style="padding:4px 8px;font-size:11px" disabled>Remap</button>
      </div>
    `).join('');
  }
}

window.addEventListener('DOMContentLoaded', () => {
  initInputPatch();
  initSweetieIntegration();
});
