// Thin API client for the Veritas backend. Dev requests are proxied to :8000.
const BASE = "/api";

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => fetch(`${BASE}/health`).then(handle),
  stats: () => fetch(`${BASE}/stats`).then(handle),

  listEvidence: (q = "") =>
    fetch(`${BASE}/evidence${q ? `?q=${encodeURIComponent(q)}` : ""}`).then(handle),

  getEvidence: (id) => fetch(`${BASE}/evidence/${id}`).then(handle),

  ingest: (formData) =>
    fetch(`${BASE}/evidence`, { method: "POST", body: formData }).then(handle),

  verify: (id) => fetch(`${BASE}/evidence/${id}/verify`, { method: "POST" }).then(handle),

  addNote: (id, payload) =>
    fetch(`${BASE}/evidence/${id}/note`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(handle),

  downloadUrl: (id) => `${BASE}/evidence/${id}/download`,
};
