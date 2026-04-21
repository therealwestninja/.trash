/**
 * i18n.js — Internationalisation: locale switching, translation lookup,
 *            language grid rendering.
 *
 * Extracted from behaviors.js. Single responsibility: text localisation.
 */

import { P, el, log } from './config.js';
import { apiFetch }    from './auth.js';

const LANGS = [
  { code: 'en', flag: '🇬🇧', name: 'English'   },
  { code: 'es', flag: '🇪🇸', name: 'Español'   },
  { code: 'fr', flag: '🇫🇷', name: 'Français'  },
  { code: 'de', flag: '🇩🇪', name: 'Deutsch'   },
  { code: 'ja', flag: '🇯🇵', name: '日本語'    },
  { code: 'zh', flag: '🇨🇳', name: '中文'      },
  { code: 'ko', flag: '🇰🇷', name: '한국어'    },
  { code: 'pt', flag: '🇧🇷', name: 'Português' },
];

// ── Translation ───────────────────────────────────────────────────────────────

/** Look up a dot-separated key in P.i18n; return raw key if not found. */
export function t(key, vars = {}) {
  const parts = key.split('.');
  let node = P.i18n;
  for (const p of parts) {
    if (typeof node !== 'object') return key;
    node = node[p];
  }
  if (typeof node !== 'string') return key;
  return node.replace(/\{(\w+)\}/g, (_, k) => vars[k] !== undefined ? vars[k] : `{${k}}`);
}

/** Apply current P.i18n strings to all [data-i18n] elements in the DOM. */
export function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.getAttribute('data-i18n');
    const v = t(k);
    if (v !== k) el.textContent = v;
  });
}

// ── Locale management ─────────────────────────────────────────────────────────

export async function loadI18n(locale) {
  if (!P.connected) { P.i18n = {}; return; }
  try {
    P.i18n   = (await apiFetch('/api/v1/i18n/translations/' + locale)) || {};
    P.locale = locale;
    applyI18n();
    log('ok', 'Language: ' + locale);
  } catch (e) { log('warn', 'i18n fetch failed: ' + e.message); }
}

export async function setLocale(code) {
  P.locale = code;
  document.querySelectorAll('.lang-opt').forEach(e =>
    e.classList.toggle('active', e.dataset.code === code)
  );
  if (P.connected) {
    try { await apiFetch('/api/v1/i18n/locale/' + code, { method: 'POST' }); } catch (_) {}
    await loadI18n(code);
  }
  log('ok', 'Language: ' + code);
}

// ── Language grid ─────────────────────────────────────────────────────────────

export function renderLangGrid() {
  const grid = el('lang-grid');
  if (!grid) return;
  grid.innerHTML = LANGS.map(l =>
    `<div class="lang-opt ${l.code === P.locale ? 'active' : ''}" data-code="${l.code}"
          onclick="window.setLocale('${l.code}')">
       <div class="lang-flag">${l.flag}</div>
       <div><div class="lang-name">${l.name}</div><div class="lang-code">${l.code}</div></div>
     </div>`
  ).join('');
}
