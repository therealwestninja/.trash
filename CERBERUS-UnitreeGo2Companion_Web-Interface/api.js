/**
 * api.js — Re-export barrel.
 *
 * All API logic has been split into focused modules:
 *   auth.js  — auth modal + apiFetch/apiPost
 *   ws.js    — WebSocket lifecycle + sendWsCmd + reconnect
 *   cmd.js   — apiCmd (REST command dispatch)
 *
 * This file exists so existing callers (behaviors.js, metrics.js, ui.js)
 * do not need to be updated in bulk. New code should import from the
 * specific module directly.
 */

export { showAuthModal, hideAuthModal, authConnect, authSkip, apiFetch, apiPost } from './auth.js';
export { connectWS, reconnectWS as reconnect, enterSimMode, sendWsCmd }           from './ws.js';
export { apiCmd }                                                                   from './cmd.js';
