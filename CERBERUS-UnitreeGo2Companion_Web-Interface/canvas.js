/**
 * canvas.js — All canvas rendering for the Companion UI.
 *
 * Three canvases:
 *   #rcanv   — isometric robot wireframe (Home tab)
 *   #acanv   — joint-angle curve visualiser (Animation Studio tab)
 *   #btcanv  — behavior tree graph (BTree tab)
 *
 * No DOM state is imported here; all data comes from function arguments
 * or the shared P state object.  This makes canvas code independently testable.
 */

import { P, el } from './config.js';

// ── Geometry helpers ──────────────────────────────────────────────────────────

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);    ctx.arcTo(x + w, y,     x + w, y + r,     r);
  ctx.lineTo(x + w, y + h - r); ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);    ctx.arcTo(x,     y + h, x,     y + h - r, r);
  ctx.lineTo(x, y + r);        ctx.arcTo(x,     y,     x + r, y,         r);
  ctx.closePath();
}

// ── Robot wireframe ───────────────────────────────────────────────────────────

export function drawRobot(tel) {
  const c = el('rcanv');
  if (!c) return;
  const ctx = c.getContext('2d');
  const W   = c.offsetWidth || 800;
  const H   = 220;
  c.width = W; c.height = H;
  ctx.clearRect(0, 0, W, H);

  // Background with subtle dot grid
  const bg = ctx.createLinearGradient(0, 0, W, H);
  bg.addColorStop(0, '#faf8f4'); bg.addColorStop(1, '#f2ede4');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(200,191,176,.3)';
  for (let x = 0; x < W; x += 24) for (let y = 0; y < H; y += 24) {
    ctx.beginPath(); ctx.arc(x, y, 1.4, 0, Math.PI * 2); ctx.fill();
  }

  const cx   = W / 2;
  const cy   = H / 2 + 8;
  const roll  = (tel?.roll_deg  || 0) * Math.PI / 180;
  const pitch = (tel?.pitch_deg || 0) * Math.PI / 180;
  const pO   = pitch * 28;  // pitch vertical offset
  const ff   = tel?.foot_forces  || { fl: 13, fr: 12, rl: 14, rr: 13 };
  const mt   = tel?.motor_temps  || { fl: 42, fr: 43, rl: 41, rr: 42 };

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(roll * 0.35);

  // Drop shadow
  ctx.save(); ctx.translate(0, 90); ctx.scale(1, 0.28);
  const sg = ctx.createRadialGradient(0, 0, 12, 0, 0, 105);
  sg.addColorStop(0, 'rgba(140,110,70,.13)'); sg.addColorStop(1, 'rgba(140,110,70,0)');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(0, 0, 105, 0, Math.PI * 2); ctx.fill();
  ctx.restore();

  // Body
  const bW = 128, bH = 54;
  ctx.fillStyle = '#fff'; ctx.strokeStyle = '#e8dfd0'; ctx.lineWidth = 2;
  roundRect(ctx, -bW / 2, -bH / 2 + pO, bW, bH, 13); ctx.fill(); ctx.stroke();
  // Centre spine line
  ctx.strokeStyle = 'rgba(200,191,176,.45)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(-bW / 2 + 18, pO); ctx.lineTo(bW / 2 - 18, pO); ctx.stroke();

  // Head bump
  ctx.fillStyle = '#faf8f4'; ctx.strokeStyle = '#e8dfd0'; ctx.lineWidth = 2;
  roundRect(ctx, bW / 2, -bH / 2 + pO, 27, 37, 7); ctx.fill(); ctx.stroke();
  // Camera eye
  ctx.fillStyle = '#4a9fd4';
  ctx.beginPath(); ctx.ellipse(bW / 2 + 13, -bH / 2 + pO + 11, 6, 6, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(bW / 2 + 15, -bH / 2 + pO + 9, 2, 0, Math.PI * 2); ctx.fill();
  // Amber LED nose
  ctx.fillStyle = '#e8913a';
  ctx.beginPath(); ctx.ellipse(bW / 2 + 21, bH / 2 + pO - 7, 5, 4, 0, 0, Math.PI * 2); ctx.fill();

  // Legs
  const active = ['performing','walking','following','navigating','patrolling'].includes(P.state);
  const phase  = Date.now() / 480;
  const legs = [
    { x: -bW / 2 + 22, y: -bH / 2 + pO + 6,  k: 'fl', label: 'FL', rear: false },
    { x:  bW / 2 - 22, y: -bH / 2 + pO + 6,  k: 'fr', label: 'FR', rear: false },
    { x: -bW / 2 + 22, y:  bH / 2 + pO - 6,  k: 'rl', label: 'RL', rear: true  },
    { x:  bW / 2 - 22, y:  bH / 2 + pO - 6,  k: 'rr', label: 'RR', rear: true  },
  ];

  legs.forEach((leg, i) => {
    const swing = active ? (leg.rear ? 0.09 : 0.04) * Math.sin(phase + (i % 2) * Math.PI) : 0;
    const tc    = mt[leg.k] > 72 ? '#e05a5a' : mt[leg.k] > 58 ? '#e8913a' : '#4caf7d';
    const ky2   = leg.y + (leg.rear ? 30 : 28) + swing * 13;
    const ky3   = ky2 + 21;
    const kx2   = leg.x + swing * 20;
    const kx3   = leg.x + swing * 10;

    // Hip socket
    ctx.fillStyle = '#e8dfd0';
    ctx.beginPath(); ctx.arc(leg.x, leg.y, 5, 0, Math.PI * 2); ctx.fill();

    // Upper leg
    ctx.strokeStyle = '#e8dfd0'; ctx.lineWidth = 6; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(leg.x, leg.y); ctx.lineTo(kx2, ky2); ctx.stroke();

    // Knee joint
    ctx.fillStyle = '#d8cfc0';
    ctx.beginPath(); ctx.arc(kx2, ky2, 4, 0, Math.PI * 2); ctx.fill();

    // Lower leg
    ctx.strokeStyle = '#d8cfc0'; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.moveTo(kx2, ky2); ctx.lineTo(kx3, ky3); ctx.stroke();

    // Foot pad (colour = temp zone)
    ctx.fillStyle = tc;
    ctx.beginPath(); ctx.arc(kx3, ky3, 5, 0, Math.PI * 2); ctx.fill();

    // Force ring
    const fv = (ff[leg.k] || 12) / 35;
    ctx.strokeStyle = tc + '88'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(kx3, ky3, 7 + fv * 4, 0, Math.PI * 2); ctx.stroke();

    // Leg label
    ctx.fillStyle = 'rgba(107,95,84,.45)';
    ctx.font = '8px "DM Sans",sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(leg.label, leg.x, leg.y - 9);
  });

  // COM dashed line
  const comX = (tel?.com_x || 0) * 280;
  ctx.strokeStyle = 'rgba(232,145,58,.55)'; ctx.lineWidth = 1.5; ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(comX, pO - 50); ctx.lineTo(comX, pO + 50); ctx.stroke();
  ctx.setLineDash([]);

  ctx.restore();

  // State label bottom-left
  ctx.fillStyle = 'rgba(107,95,84,.5)';
  ctx.font = '11px "DM Sans",sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('UNITREE GO2 — ' + P.state.toUpperCase(), 14, H - 11);
  if (P.armed) {
    ctx.fillStyle = 'rgba(76,175,125,.75)'; ctx.textAlign = 'right';
    ctx.fillText('● ARMED', W - 14, H - 11);
  }
}

// ── Animation curve canvas ────────────────────────────────────────────────────

export function drawAnimCanvas(clip, elapsedMs, neutralPose) {
  const c = el('acanv');
  if (!c) return;
  const ctx     = c.getContext('2d');
  const W       = c.offsetWidth || 800;
  const H       = 120;
  c.width = W; c.height = H;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#faf8f4'; ctx.fillRect(0, 0, W, H);

  if (!clip) {
    ctx.fillStyle = '#9e9088';
    ctx.font = '13px "DM Sans",sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('No animation loaded — select a clip below', W / 2, H / 2);
    return;
  }

  const colors  = ['#4a9fd4','#4caf7d','#e8913a','#9b7fe8','#e05a5a','#f09060'];
  const yCenter = H / 2;
  const yScale  = (H - 20) / 6;

  // Centre axis
  ctx.strokeStyle = 'rgba(200,191,176,.4)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, yCenter); ctx.lineTo(W, yCenter); ctx.stroke();

  // Draw 6 representative joint curves
  const SHOW = [0, 1, 2, 9, 10, 11];
  SHOW.forEach((ji, ci) => {
    ctx.strokeStyle = colors[ci % colors.length] + 'aa'; ctx.lineWidth = 1.5;
    ctx.beginPath();
    const steps = Math.min(200, clip.kfs.length * 3);
    for (let s = 0; s <= steps; s++) {
      const tMs = (s / steps) * clip.dur;
      const j   = _sampleClip(clip, tMs);
      const val = j[ji];
      const base = neutralPose[ji];
      const x = (s / steps) * W;
      const y = yCenter - (val - base) * yScale * 3;
      s === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
  });

  // Playhead
  if (clip.dur > 0) {
    const px = (Math.min(elapsedMs, clip.dur) / clip.dur) * W;
    ctx.strokeStyle = '#e8913a'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, H); ctx.stroke();
    ctx.fillStyle = '#e8913a';
    ctx.beginPath(); ctx.arc(px, 10, 4, 0, Math.PI * 2); ctx.fill();
  }

  // Legend
  ctx.font = '9px "DM Sans",sans-serif'; ctx.textAlign = 'left';
  ['FR_0','FR_1','FR_2','RL_0','RL_1','RL_2'].forEach((name, i) => {
    ctx.fillStyle = colors[i]; ctx.fillRect(8 + i * 70, H - 14, 10, 8);
    ctx.fillStyle = '#9e9088'; ctx.fillText(name, 22 + i * 70, H - 7);
  });
}

// ── BT graph canvas ───────────────────────────────────────────────────────────

const BT_NODES = [
  { id:'root',    label:'Selector\nroot',     type:'sel',  x:.50, y:.04, children:['emerg','mission','comp','idle'] },
  { id:'emerg',   label:'Selector\nemergency',type:'sel',  x:.14, y:.27, children:['estop_seq','avoid_seq','bat_seq'] },
  { id:'mission', label:'Sequence\nmission',  type:'seq',  x:.37, y:.27, children:['armed_c','bat_ok_c','has_m_c','run_m'] },
  { id:'comp',    label:'Sequence\ncompanion',type:'seq',  x:.64, y:.27, children:['armed_c2','human_c','follow_a'] },
  { id:'idle',    label:'Sequence\nidle',     type:'seq',  x:.87, y:.27, children:['idle_c','cooldown'] },
  { id:'estop_seq',label:'Seq\nestop',        type:'seq',  x:.05, y:.53, children:['tilt_c','estop_a'] },
  { id:'avoid_seq',label:'Seq\navoid',        type:'seq',  x:.15, y:.53, children:['obs_c','avoid_a'] },
  { id:'bat_seq', label:'Seq\nbattery',       type:'seq',  x:.25, y:.53, children:['batcrit_c','sit_a'] },
  { id:'armed_c', label:'armed?',             type:'cond', x:.31, y:.53 },
  { id:'bat_ok_c',label:'battery\nok?',       type:'cond', x:.38, y:.53 },
  { id:'has_m_c', label:'has\nmission?',      type:'cond', x:.44, y:.53 },
  { id:'run_m',   label:'run\nmission',       type:'act',  x:.50, y:.53 },
  { id:'armed_c2',label:'armed?',             type:'cond', x:.59, y:.53 },
  { id:'human_c', label:'human\nvisible?',    type:'cond', x:.66, y:.53 },
  { id:'follow_a',label:'follow',             type:'act',  x:.73, y:.53 },
  { id:'idle_c',  label:'idle?',              type:'cond', x:.84, y:.53 },
  { id:'cooldown',label:'cooldown\n5s',       type:'dec',  x:.91, y:.53 },
  { id:'tilt_c',  label:'tilted?',            type:'cond', x:.02, y:.80 },
  { id:'estop_a', label:'E-STOP',             type:'act',  x:.09, y:.80 },
  { id:'obs_c',   label:'obstacle\nclose?',   type:'cond', x:.13, y:.80 },
  { id:'avoid_a', label:'stop',               type:'act',  x:.19, y:.80 },
  { id:'batcrit_c',label:'batt\ncrit?',       type:'cond', x:.23, y:.80 },
  { id:'sit_a',   label:'sit',                type:'act',  x:.29, y:.80 },
];

const BT_TYPE_COLORS = { seq:'#4a9fd4', sel:'#9b7fe8', cond:'#4caf7d', act:'#e8913a', dec:'#f09060' };
const BT_STATUS = {};

export function simulateBTStatus() {
  const bat   = P.telemetry.battery_pct || 87;
  const pitch = Math.abs(P.telemetry.pitch_deg || 0);
  BT_STATUS.root     = P.state !== 'idle' && P.state !== 'standing' ? 'SUCCESS' : 'RUNNING';
  BT_STATUS.emerg    = pitch > 8 ? 'RUNNING' : 'FAILURE';
  BT_STATUS.mission  = P.missions?.find(m => m.status === 'running') ? 'RUNNING' : 'FAILURE';
  BT_STATUS.comp     = P.state === 'following' ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.idle     = ['idle','standing'].includes(P.state) ? 'RUNNING' : 'FAILURE';
  BT_STATUS.armed_c  = P.armed ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.armed_c2 = P.armed ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.bat_ok_c = bat > 15 ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.tilt_c   = pitch > 8 ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.batcrit_c= bat < 10 ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.human_c  = P.state === 'following' ? 'SUCCESS' : 'FAILURE';
  BT_STATUS.follow_a = P.state === 'following' ? 'RUNNING' : 'idle';
  BT_STATUS.idle_c   = ['idle','standing'].includes(P.state) ? 'SUCCESS' : 'FAILURE';
  drawBT();
}

export function drawBT() {
  const c = el('btcanv');
  if (!c) return;
  const ctx = c.getContext('2d');
  const W   = c.offsetWidth || 800;
  const H   = 280;
  c.width = W; c.height = H;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#faf8f4'; ctx.fillRect(0, 0, W, H);

  const nodeMap = {};
  BT_NODES.forEach(n => {
    nodeMap[n.id] = { ...n, px: n.x * W, py: n.y * H + 30 };
  });

  // Edges
  ctx.lineWidth = 1.5;
  BT_NODES.forEach(n => {
    if (!n.children) return;
    const par = nodeMap[n.id];
    n.children.forEach(cid => {
      const ch = nodeMap[cid]; if (!ch) return;
      const st = BT_STATUS[cid] || 'idle';
      ctx.strokeStyle = st === 'SUCCESS' ? 'rgba(76,175,125,.6)'
                      : st === 'FAILURE'  ? 'rgba(224,90,90,.6)'
                      : st === 'RUNNING'  ? 'rgba(232,145,58,.6)'
                      : 'rgba(200,191,176,.45)';
      ctx.beginPath(); ctx.moveTo(par.px, par.py + 16); ctx.lineTo(ch.px, ch.py - 16); ctx.stroke();
    });
  });

  // Nodes
  BT_NODES.forEach(n => {
    const { px, py } = nodeMap[n.id];
    const st     = BT_STATUS[n.id] || 'idle';
    const bg     = st === 'SUCCESS' ? '#e8f7ef' : st === 'FAILURE' ? '#fdeaea'
                 : st === 'RUNNING' ? '#fdf2e8' : '#f2ede4';
    const border = st === 'SUCCESS' ? '#4caf7d' : st === 'FAILURE' ? '#e05a5a'
                 : st === 'RUNNING' ? '#e8913a' : BT_TYPE_COLORS[n.type] || '#e8dfd0';
    const cr     = n.type === 'cond' || n.type === 'act' ? 8 : 10;
    ctx.fillStyle = bg; ctx.strokeStyle = border; ctx.lineWidth = 1.5;
    roundRect(ctx, px - 36, py - 14, 72, 28, cr); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#2d2620'; ctx.font = '700 8.5px "DM Sans",sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const lines = (n.label || n.id).split('\n');
    if (lines.length === 1) {
      ctx.fillText(n.label, px, py);
    } else {
      lines.forEach((l, i) => ctx.fillText(l, px, py + (i - 0.4) * 9));
    }
  });
}

// ── Clip interpolation (used by drawAnimCanvas + animation.js) ─────────────────

export function sampleClip(clip, tMs) {
  if (clip.loop && clip.dur > 0) tMs = tMs % clip.dur;
  tMs = Math.max(clip.kfs[0].t, Math.min(clip.kfs[clip.kfs.length - 1].t, tMs));
  let lo = 0, hi = clip.kfs.length - 1;
  while (lo < hi - 1) {
    const mid = (lo + hi) >> 1;
    clip.kfs[mid].t <= tMs ? (lo = mid) : (hi = mid);
  }
  if (clip.kfs[lo].t === clip.kfs[hi].t) return clip.kfs[lo].j;
  const t  = (tMs - clip.kfs[lo].t) / (clip.kfs[hi].t - clip.kfs[lo].t);
  const ts = t * t * (3 - 2 * t); // smoothstep
  return clip.kfs[lo].j.map((a, i) => a + (clip.kfs[hi].j[i] - a) * ts);
}

// Private alias used within this module
const _sampleClip = sampleClip;
