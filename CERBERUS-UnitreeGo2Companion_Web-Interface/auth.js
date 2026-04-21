/**
 * auth.js — API key management, auth modal, and authenticated fetch.
 *
 * This is the only module that knows the API key exists.
 * All other modules call apiFetch/apiPost from here.
 *
 * Single responsibility: authenticate requests and manage the auth UI.
 */

import { P, loadKey, saveKey, el, log } from './config.js';

// ── Key modal ─────────────────────────────────────────────────────────────────

export function showAuthModal() {
  const modal = el('auth-modal');
  if (!modal) return;
  modal.style.display = 'flex';
  const inp = el('auth-key-input');
  if (inp) { inp.value = loadKey(); setTimeout(() => inp.focus(), 80); }
}

export function hideAuthModal() {
  const modal = el('auth-modal');
  if (modal) modal.style.display = 'none';
}

export function authConnect() {
  const inp = el('auth-key-input');
  const key = (inp?.value || '').trim();
  saveKey(key);
  hideAuthModal();
  if (key) {
    log('ok', 'API key saved — connecting…');
    // Delegate to ws.js via window to avoid circular import.
    if (typeof window.connectWS === 'function') window.connectWS();
  } else {
    log('ok', 'No key — simulation mode');
    if (typeof window.enterSimMode === 'function') window.enterSimMode();
  }
}

export function authSkip() {
  saveKey('');
  hideAuthModal();
  if (typeof window.enterSimMode === 'function') window.enterSimMode();
}

// ── Authenticated fetch ───────────────────────────────────────────────────────

/**
 * apiFetch — injects X-CERBERUS-Key, re-prompts on 401, throws on error.
 */
export async function apiFetch(path, opts = {}) {
  const key     = loadKey();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (key) headers['X-CERBERUS-Key'] = key;

  let r;
  try {
    r = await fetch(P.apiBase + path, { ...opts, headers });
  } catch (e) {
    throw new Error('Network error: ' + e.message);
  }

  if (r.status === 401) { showAuthModal(); throw new Error('Authentication required'); }
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw new Error(d.detail || d.error || `HTTP ${r.status}`);
  }
  return r.json();
}

export async function apiPost(path, body) {
  return apiFetch(path, {
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}
