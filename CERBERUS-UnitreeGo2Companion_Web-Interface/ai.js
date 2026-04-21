/**
 * ai.js — AI-powered behavior parameter generator.
 *
 * Calls the Anthropic Messages API directly from the browser using
 * the user-supplied API key.  The key is NEVER sent to the CERBERUS
 * backend — it stays in the page's memory only.
 *
 * The generated motion parameters are displayed and can optionally
 * be sent as a custom behavior goal to the CERBERUS backend.
 */

import { P, el, log } from './config.js';
import { apiPost }     from './api.js';

export async function genAI() {
  const keyEl = el('ai-key');
  const key   = keyEl?.value.trim();
  if (!key?.startsWith('sk-')) {
    const out = el('ai-out');
    if (out) out.textContent = '// Provide a valid Anthropic API key (sk-ant-…)';
    return;
  }

  const mood = el('ai-mood')?.value  || 'playful';
  const obj  = el('ai-obj')?.value   || 'soft cushion';
  const btn  = el('ai-btn');
  const out  = el('ai-out');

  if (btn) btn.textContent = '⏳ Generating…';
  if (out) out.textContent = '// Asking Claude for motion parameters…';

  const prompt = [
    `Generate motion parameters for a Unitree Go2 robot in a "${mood}" mood`,
    `interacting with a "${obj}".`,
    `Return ONLY raw JSON (no markdown, no explanation):`,
    `{"rhythm_hz":float,"amplitude_m":float,"burst_duration_s":float,"jitter":float,"reasoning":"one sentence"}`,
    `Constraint: amplitude_m ≤ 0.08`,
  ].join(' ');

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type':    'application/json',
        'x-api-key':       key,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({
        model:      'claude-sonnet-4-20250514',
        max_tokens: 400,
        messages:   [{ role: 'user', content: prompt }],
      }),
    });

    const d   = await r.json();
    const txt = d.content?.[0]?.text || '';
    let   params;

    try {
      params = JSON.parse(txt);
    } catch {
      const m = txt.match(/\{[\s\S]*\}/);
      if (m) params = JSON.parse(m[0]);
      else throw new Error('JSON parse failed');
    }

    if (out) out.textContent = JSON.stringify(params, null, 2);
    log('ok', `AI params: rhythm=${params.rhythm_hz}Hz amp=${params.amplitude_m}m`);

    // Optionally push to backend as a custom behavior goal
    if (P.connected) {
      await apiPost('/behavior/goal', {
        name:     'ai_generated',
        priority: 0.6,
        params:   {
          rhythm_hz:        params.rhythm_hz,
          amplitude_m:      params.amplitude_m,
          burst_duration_s: params.burst_duration_s,
          jitter:           params.jitter,
          mood,
          object: obj,
        },
      }).catch(() => {});
    }

  } catch (e) {
    if (out) out.textContent = '// Error: ' + e.message;
    log('err', 'AI: ' + e.message);
  } finally {
    if (btn) btn.textContent = '✨ Generate Behavior';
  }
}
