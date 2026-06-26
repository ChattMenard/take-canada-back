// Thin API client for the Veritas backend.
// In dev, Vite proxies /api to :8000. In production, set VITE_API_BASE_URL.
const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

let authToken = localStorage.getItem("veritas_token");

export function setToken(token) {
  authToken = token;
  if (token) {
    localStorage.setItem("veritas_token", token);
  } else {
    localStorage.removeItem("veritas_token");
  }
}

export function isAuthenticated() {
  return !!authToken;
}

async function handle(res) {
  if (res.status === 401) {
    setToken(null);
    throw new Error("Authentication required");
  }
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

function authHeaders() {
  const headers = {};
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

export const api = {
  health: () => fetch(`${BASE}/health`).then(handle),
  stats: () => fetch(`${BASE}/stats`).then(handle),

  listEvidence: (q = "") =>
    fetch(`${BASE}/evidence${q ? `?q=${encodeURIComponent(q)}` : ""}`).then(handle),

  getEvidence: (id) => fetch(`${BASE}/evidence/${id}`).then(handle),

  ingest: (formData) =>
    fetch(`${BASE}/evidence`, { 
      method: "POST", 
      body: formData,
      headers: authHeaders(),
    }).then(handle),

  collectUrl: (payload) =>
    fetch(`${BASE}/evidence/collect-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),

  verify: (id) => fetch(`${BASE}/evidence/${id}/verify`, { method: "POST" }).then(handle),

  addNote: (id, payload) =>
    fetch(`${BASE}/evidence/${id}/note`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),

  downloadUrl: (id) => `${BASE}/evidence/${id}/download`,

  evidenceEntities: (id) => fetch(`${BASE}/evidence/${id}/entities`).then(handle),

  // Entities
  listEntities: (q = "") =>
    fetch(`${BASE}/entities${q ? `?q=${encodeURIComponent(q)}` : ""}`).then(handle),
  createEntity: (payload) =>
    fetch(`${BASE}/entities`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),
  deleteEntity: (id) => fetch(`${BASE}/entities/${id}`, { method: "DELETE", headers: authHeaders() }).then(handle),
  entityEvidence: (id) => fetch(`${BASE}/entities/${id}/evidence`).then(handle),
  linkEvidence: (entityId, evidenceId, role) =>
    fetch(
      `${BASE}/entities/${entityId}/link/${evidenceId}${
        role ? `?role=${encodeURIComponent(role)}` : ""
      }`,
      { method: "POST", headers: authHeaders() }
    ).then(handle),
  unlinkEvidence: (entityId, evidenceId) =>
    fetch(`${BASE}/entities/${entityId}/link/${evidenceId}`, { method: "DELETE", headers: authHeaders() }).then(handle),

  // Relationships
  listRelationships: () => fetch(`${BASE}/relationships`).then(handle),
  createRelationship: (payload) =>
    fetch(`${BASE}/relationships`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),
  deleteRelationship: (id) =>
    fetch(`${BASE}/relationships/${id}`, { method: "DELETE", headers: authHeaders() }).then(handle),
  linkRelationshipEvidence: (relationshipId, evidenceId) =>
    fetch(`${BASE}/relationships/${relationshipId}/link/${evidenceId}`, { method: "POST", headers: authHeaders() }).then(handle),
  unlinkRelationshipEvidence: (relationshipId, evidenceId) =>
    fetch(`${BASE}/relationships/${relationshipId}/link/${evidenceId}`, { method: "DELETE", headers: authHeaders() }).then(handle),

  // Timestamping (OpenTimestamps)
  timestampStatus: (id) => fetch(`${BASE}/evidence/${id}/timestamp`).then(handle),
  createTimestamp: (id) =>
    fetch(`${BASE}/evidence/${id}/timestamp`, { method: "POST", headers: authHeaders() }).then(handle),
  upgradeTimestamp: (id) =>
    fetch(`${BASE}/evidence/${id}/timestamp/upgrade`, { method: "POST", headers: authHeaders() }).then(handle),
  verifyTimestamp: (id) =>
    fetch(`${BASE}/evidence/${id}/timestamp/verify`, { method: "POST" }).then(handle),
  timestampFileUrl: (id) => `${BASE}/evidence/${id}/timestamp/file`,

  // Timeline
  listTimeline: () => fetch(`${BASE}/timeline`).then(handle),
  createTimelineEvent: (payload) =>
    fetch(`${BASE}/timeline`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),
  batchCollect: (items) =>
    fetch(`${BASE}/collect/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ items }),
    }).then(handle),

  crawlCollect: (payload) =>
    fetch(`${BASE}/collect/crawl`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),

  updateTimelineEvent: (id, payload) =>
    fetch(`${BASE}/timeline/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handle),

  deleteTimelineEvent: (id) =>
    fetch(`${BASE}/timeline/${id}`, { method: "DELETE", headers: authHeaders() }).then(handle),

  // Auth
  login: (username, password) =>
    fetch(`${BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password, grant_type: "password" }),
    }).then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      return data;
    }),
  logout: () => setToken(null),

  // Admin / Seal
  sealStatus: () => fetch(`${BASE}/admin/seal`).then(handle),
  sealVault: () => fetch(`${BASE}/admin/seal`, { method: "POST", headers: authHeaders() }).then(handle),

  // Export
  exportManifest: (vaultId) =>
    fetch(`${BASE}/export/manifest?vault_id=${encodeURIComponent(vaultId)}`, { method: "POST" }).then(handle),
  verifyAll: () => fetch(`${BASE}/export/verify-all`, { method: "POST" }).then(handle),
  exportPackage: (vaultId, includeStore) =>
    fetch(`${BASE}/export/package?vault_id=${encodeURIComponent(vaultId)}&include_store=${includeStore}`, { method: "POST" }).then(handle),
};
