# API Reference

Base URL (local dev): `http://127.0.0.1:8000`
Interactive docs (auto-generated): `http://127.0.0.1:8000/docs`

All responses are JSON unless noted. Datetimes are ISO 8601. There is currently
**no authentication** (local/trusted use).

---

## Meta

### `GET /api/health`

Liveness check.

```bash
curl http://127.0.0.1:8000/api/health
```

```json
{ "status": "ok", "version": "0.1.0" }
```

### `GET /api/stats`

Aggregate counts and storage usage.

```json
{
  "evidence_count": 1,
  "entity_count": 0,
  "relationship_count": 0,
  "timeline_count": 0,
  "storage_bytes": 926952
}
```

---

## Evidence (`/api/evidence`)

### `POST /api/evidence` — ingest

`multipart/form-data`. Hashes the file, stores it, creates the record, and logs
a `CREATED` custody event.

| Field | Required | Description |
| --- | --- | --- |
| `file` | yes | The document bytes. |
| `title` | no | Defaults to filename/hash. |
| `source_url` | no | Origin URL. |
| `source_description` | no | Free-text origin. |
| `captured_at` | no | ISO 8601; when source was captured/published. |
| `collected_by` | no | Operator/handle. |
| `notes` | no | Context. |

```bash
curl -X POST http://127.0.0.1:8000/api/evidence \
  -F "file=@report.pdf;type=application/pdf" \
  -F "title=PBO Fiscal Sustainability Report 2024" \
  -F "source_url=https://www.pbo-dpb.ca/..." \
  -F "captured_at=2024-08-28T00:00:00" \
  -F "collected_by=ChattMenard"
```

**201** returns the full `EvidenceDetail` (includes `custody_events`).
Errors: **422** empty file / bad datetime, **413** over size limit.

### `POST /api/evidence/collect-url` — one-click collect

Fetches a public URL **server-side**, then hashes, stores, and files it as
evidence (logs a `CREATED` custody event capturing HTTP status, content type,
final URL after redirects, and retrieval time).

JSON body:

| Field | Required | Description |
| --- | --- | --- |
| `url` | yes | http(s) URL to collect. |
| `title` | no | Defaults to derived filename/hash. |
| `source_description` | no | Free-text origin. |
| `captured_at` | no | ISO 8601. |
| `collected_by` | no | Operator/handle. |
| `notes` | no | Context. |

```bash
curl -X POST http://127.0.0.1:8000/api/evidence/collect-url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.pbo-dpb.ca/.../report.pdf","collected_by":"ChattMenard"}'
```

**Security (SSRF guard):** only `http`/`https` are allowed; hosts that resolve
to private, loopback, link-local, reserved, or NAT64-embedded private addresses
are refused, and **every redirect hop is re-validated**. Set
`VERITAS_ALLOW_PRIVATE_COLLECT=true` only for trusted local testing.
**422** is returned for blocked hosts, bad schemes, empty bodies, over-size
resources, too many redirects, or upstream HTTP errors.

### `GET /api/evidence` — list / search

Query params: `q` (matches title, description, notes, source_url),
`limit` (default 100, max 500), `offset` (default 0). Newest first.

```bash
curl "http://127.0.0.1:8000/api/evidence?q=pbo&limit=20"
```

Returns an array of `EvidenceRead`.

### `GET /api/evidence/{id}` — detail

Returns `EvidenceDetail` including the full custody log. **404** if not found.

### `PATCH /api/evidence/{id}` — update metadata

JSON body (any subset): `title`, `source_url`, `source_description`,
`captured_at`, `collected_by`, `notes`. Logs an `ANNOTATED` custody event.

```bash
curl -X PATCH http://127.0.0.1:8000/api/evidence/1 \
  -H "Content-Type: application/json" \
  -d '{"notes":"Cross-references 2023 FSR."}'
```

### `POST /api/evidence/{id}/note` — add custody note

JSON body: `{ "actor": "optional", "detail": "required text" }`.
Appends an `ANNOTATED` event. Returns updated `EvidenceDetail`.

### `POST /api/evidence/{id}/verify` — verify integrity

Re-reads the stored object, recomputes SHA-256, compares to the record.
Logs `VERIFIED` or `VERIFY_FAILED`.

```json
{
  "evidence_id": 1,
  "sha256": "3b077d3c...",
  "intact": true,
  "message": "Integrity confirmed: stored bytes match the recorded SHA-256."
}
```

### `GET /api/evidence/{id}/download` — export

Returns the original file (`FileResponse`) and logs an `EXPORTED` event.
**410** if the stored object is missing.

---

## Entities (`/api/entities`) — Phase 2

### `POST /api/entities`

```json
{ "name": "Example Bank", "type": "BANK", "description": "..." }
```

`type` ∈ `PERSON | BANK | AGENCY | COMPANY | OTHER`. Returns `EntityRead`.

### `GET /api/entities`

Optional `q` (name contains). Returns array ordered by name.

### `GET /api/entities/{id}` / `DELETE /api/entities/{id}`

Fetch or delete a single entity. **404** if not found; delete returns **204**.

### `POST /api/entities/{entity_id}/link/{evidence_id}`

Optional `role` query param. Links an entity to a piece of evidence.

```bash
curl -X POST "http://127.0.0.1:8000/api/entities/1/link/1?role=named%20party"
```

---

## Relationships (`/api/relationships`) — Phase 2

### `POST /api/relationships`

```json
{
  "source_entity_id": 1,
  "target_entity_id": 2,
  "kind": "CONTRACT",
  "amount": 1000000,
  "occurred_at": "2024-03-01T00:00:00",
  "description": "..."
}
```

`kind` ∈ `DONATION | CONTRACT | BOARD_SEAT | OWNERSHIP | LOBBYING | EMPLOYMENT | OTHER`.
Validates that both entities exist (**422** otherwise).

### `GET /api/relationships`

Optional `entity_id` to filter links touching that entity.

### `DELETE /api/relationships/{id}`

Returns **204**; **404** if not found.

---

## Timeline (`/api/timeline`) — Phase 3

### `POST /api/timeline`

```json
{
  "title": "Budget tabled",
  "occurred_at": "2024-04-16T00:00:00",
  "description": "...",
  "evidence_id": 1
}
```

### `GET /api/timeline`

Returns events ordered by `occurred_at`.

### `DELETE /api/timeline/{id}`

Returns **204**; **404** if not found.

---

## Error format

FastAPI's standard error envelope:

```json
{ "detail": "Evidence not found." }
```

| Code | Meaning |
| --- | --- |
| 200/201 | Success |
| 204 | Success, no content (deletes) |
| 404 | Resource not found |
| 410 | Stored object missing from vault |
| 413 | Upload exceeds size limit |
| 422 | Validation error (bad/missing fields) |
