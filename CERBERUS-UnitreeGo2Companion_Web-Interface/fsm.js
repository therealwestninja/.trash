/**
 * fsm.js — Robot FSM / behavioral state badge rendering.
 *
 * Single responsibility: translate a state string to readable UI labels
 * and update the badge, state text, and arm button accordingly.
 * Registered on window._applyFSM by main.js.
 */

import { P, el } from './config.js';

const FRIENDLY = {
  offline:     'offline',
  idle:        'resting',
  standing:    'standing',
  sitting:     'sitting',
  walking:     'going for a walk',
  following:   'following you',
  navigating:  'navigating',
  interacting: 'playing',
  performing:  'performing a trick',
  patrolling:  'on patrol',
  fault:       'needs attention ⚠️',
  estop:       'stopped 🛑',
};

export function applyFSM({ state, armed }) {
  if (state !== undefined) P.state = state;
  if (armed  !== undefined) P.armed = armed;

  const s = P.state;
  const f = FRIENDLY[s] || s;

  _set('state-friendly', e => e.textContent = f);
  _set('min-state',      e => e.textContent = f.charAt(0).toUpperCase() + f.slice(1));

  _set('main-badge', e => {
    const cls = s === 'estop' ? 'estop'
              : s === 'fault' ? 'fault'
              : s !== 'idle' && s !== 'offline' ? 'active'
              : 'idle';
    e.className   = 'sbadge ' + cls;
    e.textContent = s.charAt(0).toUpperCase() + s.slice(1);
  });

  _updateArmBtn();
}

function _updateArmBtn() {
  _set('arm-btn', b => {
    _set('arm-ico', e => e.textContent = P.armed ? '🔓' : '🔒');
    _set('arm-txt', e => e.textContent = P.armed ? 'Armed' : 'Arm');
    b.className = 'arm-btn' + (P.armed ? ' armed' : '');
  });
}

function _set(id, fn) { const e = el(id); if (e) fn(e); }
