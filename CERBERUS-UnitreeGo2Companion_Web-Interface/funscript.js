import { P, log } from './config.js';
import { sendWsCmd } from './ws.js';

/**
 * funscript.js — FunScript engine: parse, validate, interpolate, play, edit.
 *
 * FunScript is a JSON format:
 *   { "version": "1.0", "range": 90, "actions": [ {"at": ms, "pos": 0-100}, … ] }
 *
 * This engine maps "pos" (0-100 linear stroke) → Go2 body height offset,
 * giving the robot a direct physical response to the timeline.
 *
 * Architecture:
 *   FunScriptEngine  — data model, parse, validate, interpolation
 *   FunScriptPlayer  — playback clock, WS/sim output
 *   FunScriptEditor  — timeline canvas editing (add/remove/move points)
 *   renderFunScriptUI() — called by main.js to mount tab content
 *
 * Interpolation modes:
 *   linear   — straight line between keypoints
 *   smooth   — cubic Hermite (Catmull-Rom) — default
 *   step     — hold value until next point
 *
 * Safety:
 *   - pos is clamped to [SAFE_MIN, SAFE_MAX] before dispatch
 *   - Commands are rate-limited to CMD_HZ
 *   - Playback halts immediately if P.estop becomes true
 */

// ── Constants ─────────────────────────────────────────────────────────────────

const SAFE_MIN   =   0;    // pos floor (0-100 scale)
const SAFE_MAX   = 100;    // pos ceiling
const CMD_HZ     =  20;    // motion command rate during playback
const HEIGHT_MIN = -0.08;  // metres (maps to pos=0)
const HEIGHT_MAX =  0.08;  // metres (maps to pos=100)

// ── Engine — pure data & math ─────────────────────────────────────────────────

class FunScriptEngine {
  constructor() {
    this.actions      = [];   // [{at, pos}] sorted by at
    this.meta         = {};   // version, range, tags, etc.
    this.interpMode   = 'smooth';
    this._dirty       = false;
  }

  // ── Parse ──────────────────────────────────────────────────────────────────

  /**
   * Load from JSON string or parsed object.
   * Returns { ok, errors[] } — never throws.
   */
  load(raw) {
    const errors = [];
    let obj;
    if (typeof raw === 'string') {
      try { obj = JSON.parse(raw); }
      catch (e) { return { ok: false, errors: [`JSON parse error: ${e.message}`] }; }
    } else {
      obj = raw;
    }

    if (!obj || typeof obj !== 'object') return { ok: false, errors: ['Not an object'] };
    if (!Array.isArray(obj.actions))      errors.push('Missing or invalid "actions" array — attempting recovery');

    const rawActions = Array.isArray(obj.actions) ? obj.actions : [];
    const parsed     = [];
    rawActions.forEach((a, i) => {
      if (typeof a.at !== 'number' || typeof a.pos !== 'number') {
        errors.push(`Action[${i}] invalid (at=${a.at} pos=${a.pos}) — skipped`);
        return;
      }
      parsed.push({ at: Math.round(a.at), pos: Math.max(0, Math.min(100, a.pos)) });
    });

    if (!parsed.length) return { ok: false, errors: [...errors, 'No valid actions found'] };

    // Sort by time
    parsed.sort((a, b) => a.at - b.at);

    // Remove duplicate timestamps (keep last)
    this.actions = parsed.filter((a, i, arr) => i === arr.length - 1 || a.at !== arr[i + 1].at);
    this.meta    = {
      version:  obj.version || '1.0',
      range:    obj.range   || 90,
      title:    obj.title   || '',
      duration: this.actions[this.actions.length - 1].at,
    };
    this._dirty = false;
    return { ok: true, errors };
  }

  // ── Serialise ──────────────────────────────────────────────────────────────

  toJSON() {
    return JSON.stringify({
      version: this.meta.version || '1.0',
      range:   this.meta.range   || 90,
      title:   this.meta.title   || '',
      actions: this.actions.map(a => ({ at: a.at, pos: a.pos })),
    }, null, 2);
  }

  // ── Query ──────────────────────────────────────────────────────────────────

  get duration() { return this.actions.length ? this.actions[this.actions.length - 1].at : 0; }
  get length()   { return this.actions.length; }

  /**
   * Sample interpolated position [0-100] at time ms.
   */
  sample(ms) {
    if (!this.actions.length) return 50;
    if (ms <= this.actions[0].at)              return this.actions[0].pos;
    if (ms >= this.actions[this.actions.length - 1].at) return this.actions[this.actions.length - 1].pos;

    // Binary search for surrounding points
    let lo = 0, hi = this.actions.length - 1;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (this.actions[mid].at <= ms) lo = mid; else hi = mid;
    }
    const a0 = this.actions[lo], a1 = this.actions[hi];
    const t  = (ms - a0.at) / (a1.at - a0.at);   // 0..1

    if (this.interpMode === 'step')   return a0.pos;
    if (this.interpMode === 'linear') return a0.pos + (a1.pos - a0.pos) * t;

    // Smooth: Catmull-Rom via finite differences
    const pm = lo > 0 ? this.actions[lo - 1].pos : a0.pos;
    const p2 = hi < this.actions.length - 1 ? this.actions[hi + 1].pos : a1.pos;
    return _catmullRom(pm, a0.pos, a1.pos, p2, t);
  }

  // ── Editing ────────────────────────────────────────────────────────────────

  addPoint(atMs, pos) {
    atMs = Math.round(atMs);
    pos  = Math.max(0, Math.min(100, pos));
    const existing = this.actions.findIndex(a => a.at === atMs);
    if (existing >= 0) { this.actions[existing].pos = pos; }
    else {
      this.actions.push({ at: atMs, pos });
      this.actions.sort((a, b) => a.at - b.at);
    }
    this._dirty = true;
  }

  removePoint(index) {
    if (index < 0 || index >= this.actions.length) return;
    this.actions.splice(index, 1);
    this._dirty = true;
  }

  movePoint(index, newAtMs, newPos) {
    if (index < 0 || index >= this.actions.length) return;
    this.actions[index].at  = Math.round(newAtMs);
    this.actions[index].pos = Math.max(0, Math.min(100, newPos));
    this.actions.sort((a, b) => a.at - b.at);
    this._dirty = true;
  }

  /** Smooth all actions with a Gaussian blur (window = ±windowMs). */
  smooth(windowMs = 200) {
    const smoothed = this.actions.map((a, i) => {
      let sum = 0, weight = 0;
      this.actions.forEach(b => {
        const d = Math.abs(b.at - a.at);
        if (d <= windowMs) {
          const w = Math.exp(-0.5 * (d / (windowMs / 2)) ** 2);
          sum    += b.pos * w;
          weight += w;
        }
      });
      return { at: a.at, pos: weight > 0 ? sum / weight : a.pos };
    });
    this.actions = smoothed;
    this._dirty  = true;
  }
}

// ── Catmull-Rom interpolation ─────────────────────────────────────────────────

function _catmullRom(p0, p1, p2, p3, t) {
  const t2 = t * t, t3 = t2 * t;
  return 0.5 * (
    2 * p1 +
    (-p0 + p2) * t +
    (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
    (-p0 + 3 * p1 - 3 * p2 + p3) * t3
  );
}

// ── pos → hardware mapping ────────────────────────────────────────────────────

function _posToHeight(pos) {
  return HEIGHT_MIN + (pos / 100) * (HEIGHT_MAX - HEIGHT_MIN);
}

// ── Player ────────────────────────────────────────────────────────────────────

class FunScriptPlayer {
  constructor(engine) {
    this.engine    = engine;
    this.playing   = false;
    this.elapsed   = 0;
    this._t0       = 0;
    this._rafId    = null;
    this._lastCmd  = 0;
    this._cmdInt   = 1000 / CMD_HZ;
    this.onTick    = null;   // callback(ms, pos) for UI updates
    this.onEnd     = null;   // callback()
    this.loop      = false;
    this.speed     = 1.0;
  }

  play() {
    if (this.playing || !this.engine.length) return;
    this.playing = true;
    this._t0     = performance.now() - this.elapsed / this.speed;
    this._rafId  = requestAnimationFrame(this._tick.bind(this));
  }

  pause() {
    if (!this.playing) return;
    this.playing  = false;
    this.elapsed  = this._currentElapsed();
    cancelAnimationFrame(this._rafId);
    this._rafId = null;
    this._sendStop();
  }

  stop() {
    this.playing = false;
    this.elapsed = 0;
    if (this._rafId) { cancelAnimationFrame(this._rafId); this._rafId = null; }
    this._sendStop();
    this.onTick?.(0, this.engine.sample(0));
  }

  seek(ms) {
    this.elapsed = Math.max(0, Math.min(this.engine.duration, ms));
    if (this.playing) this._t0 = performance.now() - this.elapsed / this.speed;
    this.onTick?.(this.elapsed, this.engine.sample(this.elapsed));
  }

  _currentElapsed() {
    return (performance.now() - this._t0) * this.speed;
  }

  _tick(now) {
    // Safety: halt if E-stop active
    if (typeof P !== 'undefined' && P.estop) { this.pause(); return; }

    this.elapsed = this._currentElapsed();

    if (this.elapsed >= this.engine.duration) {
      if (this.loop) {
        this.elapsed = 0;
        this._t0 = performance.now();
      } else {
        this.stop();
        this.onEnd?.();
        return;
      }
    }

    const pos = Math.max(SAFE_MIN, Math.min(SAFE_MAX, this.engine.sample(this.elapsed)));
    this.onTick?.(this.elapsed, pos);

    // Rate-limited hardware output
    if (now - this._lastCmd >= this._cmdInt) {
      this._lastCmd = now;
      this._sendPos(pos);
    }

    this._rafId = requestAnimationFrame(this._tick.bind(this));
  }

  _sendPos(pos) {
    const height = _posToHeight(pos);
    if (typeof sendWsCmd === 'function') {
      if (!sendWsCmd('body_height', { height })) {
        if (typeof apiCmd === 'function') apiCmd('BODY_CTRL', { height });
      }
    }
  }

  _sendStop() {
    if (typeof sendWsCmd === 'function') sendWsCmd('stop');
  }
}

// ── Editor — canvas-based timeline ───────────────────────────────────────────

class FunScriptEditor {
  constructor(engine, player, canvasId) {
    this.engine     = engine;
    this.player     = player;
    this.canvasId   = canvasId;
    this.selected   = new Set();   // indices of selected points
    this._drag      = null;        // { index, startMs, startPos }
    this._scrollX   = 0;           // ms offset of left edge
    this._zoom      = 1.0;         // px per ms
    this._selecting = false;
    this._selRect   = null;
    this._onChanged = null;
    this._colors    = {
      bg: '#faf8f4', grid: 'rgba(200,191,176,.35)', axis: '#e8dfd0',
      curve: '#4a9fd4', curveSmooth: '#4caf7d',
      point: '#e8913a', pointSel: '#e05a5a', pointHover: '#f09060',
      playhead: '#e8913a', selRect: 'rgba(232,145,58,.15)',
    };
  }

  mount(onChanged) {
    this._onChanged = onChanged;
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    c.addEventListener('mousedown',  this._onDown.bind(this));
    c.addEventListener('mousemove',  this._onMove.bind(this));
    c.addEventListener('mouseup',    this._onUp.bind(this));
    c.addEventListener('dblclick',   this._onDbl.bind(this));
    c.addEventListener('contextmenu',this._onCtx.bind(this));
    c.addEventListener('wheel',      this._onWheel.bind(this), { passive: false });
    window.addEventListener('resize', () => this.draw());
  }

  // ── Coordinate conversion ─────────────────────────────────────────────────

  _msToX(ms, W) {
    return (ms - this._scrollX) * this._zoom;
  }
  _posToY(pos, H) {
    const PAD = 24;
    return PAD + (1 - pos / 100) * (H - PAD * 2);
  }
  _xToMs(x) { return x / this._zoom + this._scrollX; }
  _yToPos(y, H) {
    const PAD = 24;
    return Math.max(0, Math.min(100, (1 - (y - PAD) / (H - PAD * 2)) * 100));
  }

  // ── Drawing ───────────────────────────────────────────────────────────────

  draw() {
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    const ctx = c.getContext('2d');
    const W   = c.offsetWidth || 900;
    const H   = c.offsetHeight || 200;
    c.width = W; c.height = H;
    const PAD = 24;

    // Background
    ctx.fillStyle = this._colors.bg;
    ctx.fillRect(0, 0, W, H);

    // Grid lines (time)
    const gridMs = _niceGridStep(this.engine.duration / (W / 80 / this._zoom));
    ctx.strokeStyle = this._colors.grid;
    ctx.lineWidth   = 1;
    ctx.font        = '9px DM Mono,monospace';
    ctx.fillStyle   = '#9e9088';
    ctx.textAlign   = 'center';
    let tG = Math.floor(this._scrollX / gridMs) * gridMs;
    while (tG < this._scrollX + W / this._zoom) {
      const x = this._msToX(tG, W);
      if (x >= 0 && x <= W) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        ctx.fillText(_fmtMs(tG), x, H - 6);
      }
      tG += gridMs;
    }

    // Pos grid lines (25/50/75)
    [25, 50, 75].forEach(p => {
      const y = this._posToY(p, H);
      ctx.strokeStyle = this._colors.grid;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      ctx.fillStyle = '#c8bfb0';
      ctx.textAlign = 'left';
      ctx.fillText(p, 3, y - 2);
    });

    if (!this.engine.length) {
      ctx.fillStyle = '#9e9088';
      ctx.font = '13px DM Sans,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No script loaded — import a .funscript file or right-click to add points', W / 2, H / 2);
      return;
    }

    // Smooth curve
    ctx.strokeStyle = this._colors.curve;
    ctx.lineWidth   = 2;
    ctx.beginPath();
    const steps = Math.min(W * 2, 2000);
    for (let s = 0; s <= steps; s++) {
      const ms = this._scrollX + (s / steps) * (W / this._zoom);
      if (ms < 0 || ms > this.engine.duration + 50) continue;
      const pos = this.engine.sample(ms);
      const x   = this._msToX(ms, W);
      const y   = this._posToY(pos, H);
      s === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Fill under curve
    ctx.fillStyle = 'rgba(74,159,212,.07)';
    ctx.lineTo(this._msToX(this.engine.duration, W), H);
    ctx.lineTo(this._msToX(0, W), H);
    ctx.fill();

    // Selection rectangle
    if (this._selRect) {
      ctx.fillStyle   = this._colors.selRect;
      ctx.strokeStyle = '#e8913a';
      ctx.lineWidth   = 1;
      const r = this._selRect;
      ctx.fillRect(r.x, r.y, r.w, r.h);
      ctx.strokeRect(r.x, r.y, r.w, r.h);
    }

    // Control points
    this.engine.actions.forEach((a, i) => {
      const x    = this._msToX(a.at, W);
      const y    = this._posToY(a.pos, H);
      if (x < -8 || x > W + 8) return;
      const sel  = this.selected.has(i);
      const rad  = sel ? 7 : 5;
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fillStyle   = sel ? this._colors.pointSel : this._colors.point;
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth   = 1.5;
      ctx.stroke();
    });

    // Playhead
    if (this.player.elapsed >= 0 && this.engine.duration > 0) {
      const px = this._msToX(this.player.elapsed, W);
      if (px >= 0 && px <= W) {
        ctx.strokeStyle = this._colors.playhead;
        ctx.lineWidth   = 2;
        ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
        ctx.fillStyle = this._colors.playhead;
        ctx.beginPath(); ctx.arc(px, 12, 5, 0, Math.PI * 2); ctx.fill();
      }
    }
  }

  // ── Mouse interactions ────────────────────────────────────────────────────

  _hitTest(x, y, H) {
    const R = 10;
    for (let i = this.engine.actions.length - 1; i >= 0; i--) {
      const a   = this.engine.actions[i];
      const ax  = this._msToX(a.at);
      const ay  = this._posToY(a.pos, H);
      if (Math.hypot(x - ax, y - ay) <= R) return i;
    }
    return -1;
  }

  _onDown(e) {
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;
    const H    = c.height;
    const hit  = this._hitTest(mx, my, H);

    if (hit >= 0) {
      if (e.shiftKey) {
        this.selected.has(hit) ? this.selected.delete(hit) : this.selected.add(hit);
      } else {
        if (!this.selected.has(hit)) { this.selected.clear(); this.selected.add(hit); }
      }
      this._drag = { indices: [...this.selected], startX: mx, startY: my,
        origPts: [...this.selected].map(i => ({ ...this.engine.actions[i] })) };
    } else {
      if (!e.shiftKey) this.selected.clear();
      this._selStart = { x: mx, y: my };
    }
    this.draw();
  }

  _onMove(e) {
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;
    const H    = c.height;

    if (this._drag) {
      const dMs  = (mx - this._drag.startX) / this._zoom;
      const dPos = -(my - this._drag.startY) / (H - 48) * 100;
      this._drag.indices.forEach((idx, i) => {
        const orig = this._drag.origPts[i];
        this.engine.movePoint(idx, orig.at + dMs, orig.pos + dPos);
      });
      this._onChanged?.();
    } else if (this._selStart) {
      const x = Math.min(mx, this._selStart.x);
      const y = Math.min(my, this._selStart.y);
      const w = Math.abs(mx - this._selStart.x);
      const h = Math.abs(my - this._selStart.y);
      this._selRect = { x, y, w, h };
      // Select all points inside rect
      this.engine.actions.forEach((a, i) => {
        const ax = this._msToX(a.at);
        const ay = this._posToY(a.pos, H);
        if (ax >= x && ax <= x + w && ay >= y && ay <= y + h) this.selected.add(i);
      });
    }
    this.draw();
  }

  _onUp() {
    this._drag     = null;
    this._selStart = null;
    this._selRect  = null;
    this.draw();
  }

  _onDbl(e) {
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const mx   = e.clientX - rect.left;
    const my   = e.clientY - rect.top;
    const H    = c.height;
    const hit  = this._hitTest(mx, my, H);
    if (hit >= 0) {
      this.engine.removePoint(hit);
      this.selected.delete(hit);
    } else {
      const ms  = this._xToMs(mx);
      const pos = this._yToPos(my, H);
      this.engine.addPoint(ms, pos);
    }
    this._onChanged?.();
    this.draw();
  }

  _onCtx(e) {
    e.preventDefault();
    const c = document.getElementById(this.canvasId);
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const ms   = this._xToMs(e.clientX - rect.left);
    const pos  = this._yToPos(e.clientY - rect.top, c.height);
    this.engine.addPoint(ms, pos);
    this._onChanged?.();
    this.draw();
  }

  _onWheel(e) {
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) {
      // Zoom
      const c    = document.getElementById(this.canvasId);
      const rect = c.getBoundingClientRect();
      const mx   = e.clientX - rect.left;
      const msAt = this._xToMs(mx);
      this._zoom  = Math.max(0.05, Math.min(5, this._zoom * (e.deltaY < 0 ? 1.2 : 0.83)));
      this._scrollX = msAt - mx / this._zoom;
    } else {
      this._scrollX = Math.max(0, this._scrollX + e.deltaY * 50 / this._zoom);
    }
    this.draw();
  }
}

// ── Formatting helpers ────────────────────────────────────────────────────────

function _fmtMs(ms) {
  if (ms < 1000) return ms + 'ms';
  return (ms / 1000).toFixed(1) + 's';
}

function _niceGridStep(raw) {
  const candidates = [50,100,250,500,1000,2000,5000,10000,30000,60000];
  return candidates.find(v => v >= raw) || 60000;
}

// ── Public module state ───────────────────────────────────────────────────────

const _engine = new FunScriptEngine();
const _player = new FunScriptPlayer(_engine);
let   _editor = null;

// ── Public API (called from main.js / HTML) ───────────────────────────────────

function fsPlay()  { _player.play();  _updateFSUI(); }
function fsPause() { _player.pause(); _updateFSUI(); }
function fsStop()  { _player.stop();  _updateFSUI(); }

function fsSetSpeed(v) {
  _player.speed = parseFloat(v) || 1;
  const el = document.getElementById('fs-speed-val');
  if (el) el.textContent = _player.speed.toFixed(2) + '×';
}

function fsSetLoop(v) { _player.loop = !!v; }

function fsSetInterp(mode) {
  _engine.interpMode = mode;
  _editor?.draw();
  _updateFSStats();
}

function fsSmooth() {
  _engine.smooth(250);
  _editor?.draw();
  _logFS('ok', 'Applied smoothing');
}

function fsDeleteSelected() {
  if (!_editor) return;
  const indices = [..._editor.selected].sort((a, b) => b - a);
  indices.forEach(i => _engine.removePoint(i));
  _editor.selected.clear();
  _editor.draw();
  _updateFSStats();
}

function fsExport() {
  if (!_engine.length) { _logFS('warn', 'Nothing to export'); return; }
  const blob = new Blob([_engine.toJSON()], { type: 'application/json' });
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = (_engine.meta.title || 'script') + '_' + Date.now() + '.funscript';
  a.click();
  _logFS('ok', 'Exported ' + _engine.length + ' actions');
}

function fsImport() {
  const inp = document.getElementById('fs-file-input');
  if (inp) inp.click();
}

function fsHandleFile(e) {
  const file = e.target?.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const result = _engine.load(ev.target.result);
    if (result.errors.length) result.errors.forEach(err => _logFS('warn', err));
    if (result.ok) {
      _logFS('ok', `Loaded "${_engine.meta.title || file.name}" — ${_engine.length} pts, ${_fmtMs(_engine.duration)}`);
      _player.stop();
      _editor?.draw();
      _updateFSUI();
      _updateFSStats();
    } else {
      _logFS('err', 'Load failed: ' + result.errors.join('; '));
    }
  };
  reader.readAsText(file);
}

function fsGenerateSine() {
  _engine.actions = [];
  const dur = 10000;
  for (let ms = 0; ms <= dur; ms += 100) {
    const pos = 50 + 40 * Math.sin(2 * Math.PI * ms / 2000);
    _engine.addPoint(ms, pos);
  }
  _engine.meta = { version: '1.0', range: 90, title: 'Sine Test', duration: dur };
  _player.stop();
  _editor?.draw();
  _updateFSUI();
  _updateFSStats();
  _logFS('ok', 'Generated 10s sine wave (' + _engine.length + ' pts)');
}

// ── Mount / render ─────────────────────────────────────────────────────────────

/**
 * renderFunScriptUI() — called once to build the FunScript tab DOM and wire events.
 * Safe to call multiple times (idempotent).
 */
function renderFunScriptUI() {
  const tab = document.getElementById('tab-funscript');
  if (!tab || tab.dataset.mounted) return;
  tab.dataset.mounted = '1';

  tab.innerHTML = `
    <!-- Header -->
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
      <div>
        <div class="page-title">FunScript Engine</div>
        <div class="page-sub" id="fs-meta">No script loaded</div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn btn-ghost" onclick="fsImport()" style="font-size:12px">📂 Import</button>
        <button class="btn btn-ghost" onclick="fsExport()" style="font-size:12px">💾 Export</button>
        <button class="btn btn-ghost" onclick="fsGenerateSine()" style="font-size:12px">〜 Test Sine</button>
        <input type="file" id="fs-file-input" accept=".funscript,.json" style="display:none" onchange="fsHandleFile(event)">
      </div>
    </div>

    <!-- Timeline editor canvas -->
    <div class="card" style="padding:0;overflow:hidden">
      <div style="display:flex;align-items:center;gap:10px;padding:10px 14px 0;flex-wrap:wrap">
        <span style="font-size:11px;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em">Timeline Editor</span>
        <span style="font-size:10px;color:var(--muted)">Right-click to add · Double-click point to remove · Drag to move · Scroll to pan · Ctrl+Scroll to zoom · Shift+click multi-select</span>
      </div>
      <canvas id="fs-canvas" style="width:100%;height:220px;display:block;cursor:crosshair"></canvas>
      <div style="display:flex;gap:8px;padding:8px 14px;border-top:1px solid var(--tan);flex-wrap:wrap;align-items:center">
        <button class="btn btn-ghost" style="padding:4px 11px;font-size:12px" onclick="fsDeleteSelected()">🗑 Del</button>
        <button class="btn btn-ghost" style="padding:4px 11px;font-size:12px" onclick="fsSmooth()">〰 Smooth</button>
        <label style="font-size:11px;color:var(--ink3);margin-left:8px">Interp:</label>
        <select onchange="fsSetInterp(this.value)" style="font-size:11px;padding:3px 7px;border:1px solid var(--tan);border-radius:6px;background:var(--cream)">
          <option value="smooth" selected>Smooth (Catmull-Rom)</option>
          <option value="linear">Linear</option>
          <option value="step">Step</option>
        </select>
        <span style="margin-left:auto;font-size:11px;font-family:var(--mono);color:var(--ink3)" id="fs-stats">0 pts · 0s</span>
      </div>
    </div>

    <!-- Playback controls -->
    <div class="card" style="display:flex;align-items:center;gap:12px;padding:12px 16px;flex-wrap:wrap">
      <button class="btn btn-p"     id="fs-play-btn" onclick="fsPlay()"  style="padding:7px 20px">▶ Play</button>
      <button class="btn btn-ghost" onclick="fsPause()"                  style="padding:7px 14px">⏸</button>
      <button class="btn btn-ghost" onclick="fsStop()"                   style="padding:7px 14px">⏹</button>
      <div style="flex:1;min-width:120px">
        <div class="anim-timeline" id="fs-tl" onclick="fsScrub(event)" style="cursor:pointer">
          <div class="anim-head" id="fs-head" style="width:0%"></div>
        </div>
      </div>
      <span style="font-family:var(--mono);font-size:11px;color:var(--ink3);min-width:90px;text-align:right" id="fs-time">0.0s / 0.0s</span>
      <label style="font-size:11px;color:var(--ink3)">Speed</label>
      <input type="range" min="0.1" max="3" step="0.05" value="1" oninput="fsSetSpeed(+this.value)" style="width:72px">
      <span id="fs-speed-val" style="font-family:var(--mono);font-size:11px;color:var(--ambD);min-width:32px">1.00×</span>
      <label class="toggle"><input type="checkbox" id="fs-loop" onchange="fsSetLoop(this.checked)"><span class="ttrack"></span></label>
      <span style="font-size:11px;color:var(--ink3)">Loop</span>
    </div>

    <!-- Hardware output status -->
    <div class="card" style="padding:10px 16px">
      <div class="ctitle" style="margin-bottom:8px"><span class="ci">🤖</span>Hardware Output</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
        <div class="tcell"><div class="tlbl">Mode</div><div class="tval" id="fs-mode">Simulation</div></div>
        <div class="tcell"><div class="tlbl">Current pos</div><div class="tval" id="fs-curpos">50</div></div>
        <div class="tcell"><div class="tlbl">Height out</div><div class="tval" id="fs-height">0.00m</div></div>
      </div>
    </div>

    <!-- Log -->
    <div id="fs-log" style="font-family:var(--mono);font-size:10px;color:var(--ink3);max-height:80px;overflow-y:auto;padding:4px 0"></div>
  `;

  // Wire player callbacks
  _player.onTick = (ms, pos) => {
    const dur  = _engine.duration || 1;
    const pct  = Math.min(100, (ms / dur) * 100);
    const head = document.getElementById('fs-head');
    const time = document.getElementById('fs-time');
    const cp   = document.getElementById('fs-curpos');
    const ht   = document.getElementById('fs-height');
    if (head) head.style.width = pct + '%';
    if (time) time.textContent = (ms / 1000).toFixed(2) + 's / ' + (dur / 1000).toFixed(1) + 's';
    if (cp)   cp.textContent   = Math.round(pos);
    if (ht)   ht.textContent   = _posToHeight(pos).toFixed(3) + 'm';
    _editor?.draw();
  };
  _player.onEnd = () => {
    _logFS('ok', 'Playback complete');
    _updateFSUI();
  };

  // Build editor
  _editor = new FunScriptEditor(_engine, _player, 'fs-canvas');
  _editor.mount(() => { _updateFSStats(); });

  // Scrub click on timeline bar
  window.fsScrub = fsScrub;

  _editor.draw();
}

function fsScrub(e) {
  const bar  = document.getElementById('fs-tl');
  if (!bar) return;
  const rect = bar.getBoundingClientRect();
  const t    = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  _player.seek(t * _engine.duration);
}

function _updateFSUI() {
  const btn = document.getElementById('fs-play-btn');
  if (btn) btn.textContent = _player.playing ? '⏸ Playing' : '▶ Play';
  const dur = _engine.duration || 0;
  const meta = document.getElementById('fs-meta');
  if (meta) meta.textContent = _engine.meta.title
    ? `"${_engine.meta.title}" · ${_engine.length} pts · ${_fmtMs(dur)}`
    : (_engine.length ? `${_engine.length} pts · ${_fmtMs(dur)}` : 'No script loaded');
  const modeEl = document.getElementById('fs-mode');
  if (modeEl) {
    modeEl.textContent = (typeof P !== 'undefined' && P.connected) ? '🟢 Live hardware' : '🔵 Simulation';
  }
}

function _updateFSStats() {
  const el = document.getElementById('fs-stats');
  if (el) el.textContent = `${_engine.length} pts · ${_fmtMs(_engine.duration)}`;
}

function _logFS(level, msg) {
  const box = document.getElementById('fs-log');
  if (!box) return;
  const ts   = new Date().toTimeString().slice(0, 8);
  const div  = document.createElement('div');
  div.style.color = level === 'err' ? 'var(--rose)' : level === 'ok' ? 'var(--leaf)' : 'var(--ink3)';
  div.textContent = `[${ts}] ${msg}`;
  box.prepend(div);
  if (box.children.length > 40) box.removeChild(box.lastChild);
  if (typeof log === 'function') log(level, 'FS: ' + msg);
}

export { renderFunScriptUI, fsPlay, fsPause, fsStop, fsSetSpeed, fsSetLoop, fsSetInterp, fsSmooth, fsDeleteSelected, fsExport, fsImport, fsHandleFile, fsGenerateSine, fsScrub };
