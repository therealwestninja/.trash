/**
 * animation.js — Animation clip system.
 *
 * Handles: clip generation, playback state, timeline UI, format
 * import/export, and the animation canvas tick.
 *
 * The canvas itself is drawn by canvas.js (drawAnimCanvas);
 * this module manages the data and timing.
 */

import { P, el, log } from './config.js';
import { sampleClip, drawAnimCanvas } from './canvas.js';
import { apiFetch } from './api.js';

// ── Neutral joint pose (12-DOF: 4 legs × 3 joints) ───────────────────────────

export const NEUTRAL_POSE  = [0, 0.67, -1.30, 0, 0.67, -1.30, 0, 0.67, -1.30, 0, 0.67, -1.30];
export const ENGAGE_POSE   = [0, 0.80, -1.50, 0, 0.80, -1.50, 0, 0.40, -0.90, 0, 0.40, -0.90];
export const SIT_POSE      = [0, 0.67, -1.30, 0, 0.67, -1.30, 0, 1.60, -2.40, 0, 1.60, -2.40];

// ── Built-in procedural clip generators ───────────────────────────────────────

function genBreathing() {
  const kfs = [];
  for (let i = 0; i <= 80; i++) {
    const ph = 2 * Math.PI * (i / 80);
    const off = 0.02 * Math.sin(ph);
    kfs.push({ t: i * 50, j: NEUTRAL_POSE.map((v, k) => k % 3 === 1 ? v + off * 0.5 : k % 3 === 2 ? v - off : v) });
  }
  return { id: 'idle_breath', name: 'Breathing', dur: 4000, kfs, loop: true };
}

function genTailWag() {
  const kfs = [];
  for (let i = 0; i <= 60; i++) {
    const ph = 4 * Math.PI * (i / 60);
    const j = [...NEUTRAL_POSE];
    j[9] = 0.15 * Math.sin(ph); j[6] = 0.15 * Math.sin(ph + Math.PI);
    kfs.push({ t: i * 33, j });
  }
  return { id: 'tail_wag', name: 'Happy Wag', dur: 2000, kfs, loop: false };
}

function genHeadTilt() {
  const kfs = [];
  for (let i = 0; i <= 45; i++) {
    const t = i / 45;
    const tilt = t < 0.2 ? t / 0.2 : t < 0.7 ? 1.0 : (1 - t) / 0.3;
    const ts = tilt * tilt * (3 - 2 * tilt);
    const off = 0.12 * ts;
    const j = [...NEUTRAL_POSE]; j[3] = -off; j[9] = -off * 0.5;
    kfs.push({ t: i * 33, j });
  }
  return { id: 'head_tilt', name: 'Head Tilt', dur: 1500, kfs, loop: false };
}

function genSitDown() {
  const kfs = [];
  for (let i = 0; i <= 30; i++) {
    const ts = (i / 30); const sm = ts * ts * (3 - 2 * ts);
    const j = NEUTRAL_POSE.map((v, k) => v + (SIT_POSE[k] - v) * sm);
    kfs.push({ t: (1500 / 30) * i, j });
  }
  return { id: 'sit_down', name: 'Sit Down', dur: 1500, kfs, loop: false };
}

// ── Playback state ────────────────────────────────────────────────────────────

let _startT   = 0;
let _pauseElapsed = 0;

export function getAnimElapsed() {
  if (!P.anim.playing) return _pauseElapsed;
  return _pauseElapsed + (Date.now() - _startT) * P.anim.speed;
}

// ── Init — populate built-in clips ────────────────────────────────────────────

export function initAnimation() {
  P.anim.clips = {
    idle_breath: genBreathing(),
    tail_wag:    genTailWag(),
    head_tilt:   genHeadTilt(),
    sit_down:    genSitDown(),
  };
}

// ── Playback controls (called from HTML onclick handlers) ─────────────────────

export function animLoad(id) {
  const clip = P.anim.clips[id];
  if (!clip) return;
  P.anim.current = clip;
  P.anim.playing = false;
  _pauseElapsed  = 0;
  _updateAnimUI();
  log('ok', 'Loaded: ' + clip.name);
  renderAnimClipList();
}

export function animPlay() {
  if (!P.anim.current) { log('warn', 'No animation loaded'); return; }
  if (P.anim.playing) return;
  _startT = Date.now();
  P.anim.playing = true;
  const btn = el('anim-play-btn');
  if (btn) btn.innerHTML = '⏸ Playing';
  log('ok', 'Animation playing: ' + P.anim.current.name);
  if (P.connected) {
    apiFetch('/api/v1/animations/' + P.anim.current.id + '/play', {
      method: 'POST', body: JSON.stringify({ speed: P.anim.speed }),
    }).catch(() => {});
  }
}

export function animPause() {
  if (!P.anim.playing) return;
  _pauseElapsed = getAnimElapsed();
  P.anim.playing = false;
  const btn = el('anim-play-btn');
  if (btn) btn.innerHTML = '▶ Play';
}

export function animStop() {
  P.anim.playing = false;
  _pauseElapsed = 0;
  _updateAnimUI();
}

export function animSetSpeed(v) {
  P.anim.speed = v;
  const sv = el('anim-speed-val');
  if (sv) sv.textContent = v + '×';
}

export function animSetLoop(v) {
  if (P.anim.current) P.anim.current.loop = v;
}

export function animSeek(ev) {
  if (!P.anim.current) return;
  const tl   = el('anim-tl');
  const rect = tl.getBoundingClientRect();
  const t    = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
  _pauseElapsed = t * P.anim.current.dur;
  const head = el('anim-head');
  if (head) head.style.width = (t * 100) + '%';
}

// Called from simulation.js animTick
export function animTick() {
  if (P.anim.playing && P.anim.current) {
    const elapsed = getAnimElapsed();
    if (elapsed >= P.anim.current.dur) {
      if (P.anim.current.loop) {
        _pauseElapsed = 0; _startT = Date.now();
      } else {
        animStop();
        log('ok', 'Animation complete: ' + P.anim.current.name);
      }
    }
  }
  drawAnimCanvas(P.anim.current, getAnimElapsed(), NEUTRAL_POSE);
}

// ── File import / export ──────────────────────────────────────────────────────

export function loadAnimFormat(fmt) {
  const inp = el('anim-file-input');
  if (inp) { inp.dataset.fmt = fmt; inp.click(); }
}

export async function handleAnimFile(e) {
  const f = e.target.files[0]; if (!f) return;
  const fmt  = e.target.dataset.fmt || 'json';
  const text = await f.text();

  if (P.connected) {
    try {
      const r = await apiFetch('/api/v1/animations/load', {
        method: 'POST',
        body: JSON.stringify({ content: text, format: fmt, name: f.name.replace(/\.[^.]+$/, '') }),
      });
      log('ok', 'Uploaded: ' + r.id);
    } catch (err) { log('err', 'Upload failed: ' + err.message); }
    return;
  }

  // Browser-side parse (FunScript only for now)
  try {
    if (fmt === 'funscript' || fmt === 'json') {
      const data = JSON.parse(text);
      if (fmt === 'funscript' && data.actions) {
        const acts = data.actions;
        const dur  = acts[acts.length - 1].at;
        const kfs  = acts.map(a => ({
          t: a.at,
          j: NEUTRAL_POSE.map((v, k) => v + (ENGAGE_POSE[k] - v) * (a.pos / 100)),
        }));
        const clip = { id: 'loaded', name: f.name.replace(/\.[^.]+$/, ''), dur, kfs, loop: false };
        P.anim.clips.loaded = clip;
        animLoad('loaded');
        return;
      }
    }
    log('warn', 'Browser parsing limited — connect to backend for full format support');
  } catch (err) { log('err', 'Parse failed: ' + err.message); }
}

export function exportAnim(fmt) {
  const c = P.anim.current;
  if (!c) { log('warn', 'No animation loaded'); return; }
  let data, ext;
  if (fmt === 'funscript') {
    data = {
      version: '1.0', range: 90,
      actions: c.kfs.map(kf => ({
        at: Math.round(kf.t),
        pos: Math.round((kf.j[8] - NEUTRAL_POSE[8]) / (ENGAGE_POSE[8] - NEUTRAL_POSE[8]) * 100),
      })),
    };
    ext = 'funscript';
  } else {
    data = { name: c.name, loop: c.loop, keyframes: c.kfs.map(kf => ({ time_ms: Math.round(kf.t), joints: kf.j.map(v => Math.round(v * 1000) / 1000) })) };
    ext = 'json';
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  a.download = c.name + '_' + Date.now() + '.' + ext;
  a.click();
  log('ok', 'Exported as ' + ext);
}

// ── Clip list renderer ────────────────────────────────────────────────────────

export function renderAnimClipList() {
  const list  = el('anim-clips-list');
  if (!list) return;
  const clips = Object.values(P.anim.clips);
  if (!clips.length) { list.innerHTML = ''; return; }
  list.innerHTML = `
    <div class="card">
      <div class="ctitle"><span class="ci">🎞</span>Loaded Clips (${clips.length})</div>
      ${clips.map(c => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--cream)">
          <div>
            <div style="font-size:12px;font-weight:500;color:var(--ink)">${c.name}</div>
            <div style="font-size:10px;color:var(--ink3)">${c.kfs.length} kf · ${(c.dur / 1000).toFixed(1)}s${c.loop ? ' · loop' : ''}</div>
          </div>
          <button class="btn btn-ghost" style="padding:4px 9px;font-size:11px" onclick="window.animLoad('${c.id}')">Load</button>
        </div>`).join('')}
    </div>`;
}

// ── Internal helpers ──────────────────────────────────────────────────────────

function _updateAnimUI() {
  const btn  = el('anim-play-btn');
  const head = el('anim-head');
  const time = el('anim-time');
  const name = el('anim-clip-name');
  const dur  = P.anim.current ? (P.anim.current.dur / 1000).toFixed(1) : '0.0';
  if (btn)  btn.innerHTML   = '▶ Play';
  if (head) head.style.width = '0%';
  if (time) time.textContent = `0.0s / ${dur}s`;
  if (name) name.textContent = P.anim.current ? P.anim.current.name : 'No animation loaded';
}
