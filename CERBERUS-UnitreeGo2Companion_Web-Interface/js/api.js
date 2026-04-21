const API_BASE = "/api/v1";

async function apiGet(path) {
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json" }
  });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.error?.message || data?.detail || `POST ${path} failed: ${res.status}`);
  }
  return data;
}
