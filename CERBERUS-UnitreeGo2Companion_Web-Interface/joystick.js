const CLAMP = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

function makeJoystick(baseId, knobId, valsId, onMove, onRelease) {
  const base = document.getElementById(baseId);
  const knob = document.getElementById(knobId);
  const vals = document.getElementById(valsId);
  if (!base || !knob) return null;
  let active = false, pointerId = null, cx = 0, cy = 0;
  const getRadius = () => base.offsetWidth / 2;
  function updateKnob(nx, ny) {
    const radius = getRadius();
    const px = nx * radius * 0.6;
    const py = ny * radius * 0.6;
    knob.style.transform = `translate(calc(-50% + ${px}px), calc(-50% + ${py}px))`;
    knob.classList.toggle('active', Math.abs(nx) > 0.05 || Math.abs(ny) > 0.05);
  }
  function reset() {
    active = false; pointerId = null; updateKnob(0,0); if (vals) vals.textContent = onRelease?.label ?? ''; onMove(0,0); onRelease?.fn?.();
  }
  function pointerMove(e) {
    if (!active) return;
    if (pointerId !== null && e.pointerId !== pointerId) return;
    e.preventDefault?.();
    const radius = getRadius();
    const dx = e.clientX - cx, dy = e.clientY - cy;
    const dist = Math.hypot(dx, dy);
    const scale = dist > radius ? radius / dist : 1;
    const nx = CLAMP(dx * scale / radius, -1, 1);
    const ny = CLAMP(dy * scale / radius, -1, 1);
    updateKnob(nx, ny);
    if (vals) vals.textContent = onRelease?.valFmt?.(nx, ny) ?? `${nx.toFixed(2)}, ${ny.toFixed(2)}`;
    onMove(nx, ny);
  }
  base.addEventListener('pointerdown', e => { active = true; pointerId = e.pointerId ?? null; const r=base.getBoundingClientRect(); cx=r.left+r.width/2; cy=r.top+r.height/2; base.setPointerCapture?.(e.pointerId); e.preventDefault(); }, { passive: false });
  base.addEventListener('pointermove', pointerMove, { passive: false });
  base.addEventListener('pointerup', reset);
  base.addEventListener('pointercancel', reset);
  document.addEventListener('mousemove', e => { if (!active || pointerId !== null) return; pointerMove({ clientX: e.clientX, clientY: e.clientY, preventDefault(){} }); });
  document.addEventListener('mouseup', () => { if (active && pointerId === null) reset(); });
}

export function initJoystick() {
  makeJoystick('js-base', 'js-knob', 'js-vals',
    (nx, ny) => { window._inputSetJoystickL?.(nx, ny); const el=document.getElementById('js-vals'); if (el) el.textContent=`vx: ${(-ny).toFixed(2)}  vy: ${nx.toFixed(2)}`; },
    { fn: () => window._inputSetJoystickL?.(0,0), label: 'vx: 0.00  vy: 0.00' }
  );
  makeJoystick('js-base-r', 'js-knob-r', 'js-vals-r',
    (nx, ny) => { window._inputSetJoystickR?.(nx, ny); const el=document.getElementById('js-vals-r'); if (el) el.textContent=`yaw: ${nx.toFixed(2)}`; },
    { fn: () => window._inputSetJoystickR?.(0,0), label: 'yaw: 0.00' }
  );
}
