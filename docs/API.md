# API Reference

Base URL (local dev): `http://127.0.0.1:8000`
Interactive docs (auto-generated): `http://127.0.0.1:8000/docs`

All responses are JSON unless noted. Datetimes are ISO 8601. Write operations
require JWT authentication via `POST /api/auth/token` (default admin credentials
`admin` / `admin`; change via `VERITAS_ADMIN_PASSWORD`).

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
evidence. Logs a `CREATED` custody event capturing HTTP status, content type,
final URL after redirects, retrieval time, and (for the Playwright fallback
path) a rendered PNG screenshot. HTTP response headers are also saved as a
companion file at `<sha256>.headers.json`; screenshots are saved as
`<sha256>.screenshot.png` alongside the object.

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

### `GET /api/evidence/{id}/entities` — linked entities

Returns the entities linked to this evidence, with optional `role`.

```json
[
  { "id": 1, "name": "Bank of Canada", "type": "AGENCY", "role": "subject" }
]
```

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

### `GET /api/evidence/{id}/screenshot`

Returns the PNG screenshot captured at URL collection time (only available if
the Playwright fallback path was used). **404** if no screenshot exists.

### `GET /api/evidence/{id}/headers`

Returns the HTTP response headers captured at URL collection time as JSON.
**404** if no captured headers exist.

### `GET /api/evidence/{id}/timestamp`

Returns timestamp status:

```json
{ "evidence_id": 1, "sha256": "abcd...", "timestamped": true }
```

### `POST /api/evidence/{id}/timestamp`

Create an OpenTimestamps signature for the evidence hash. Stores a detached
`.ots` file in `backend/data/timestamps/`. Returns **503** if timestamping is
disabled or no calendar responds.

### `GET /api/evidence/{id}/timestamp/file`

Download the detached `.ots` file.

### `POST /api/evidence/{id}/timestamp/upgrade`

Re-submit the hash to OpenTimestamps calendars to pick up Bitcoin confirmations.

### `POST /api/evidence/{id}/timestamp/verify`

Verify the timestamp against the Bitcoin blockchain via the Blockstream.info API.

```json
{
  "evidence_id": 1,
  "sha256": "abcd...",
  "verified": true,
  "pending": false,
  "attestations": [{ "type": "bitcoin", "height": 800000 }],
  "block_height": 800000,
  "block_hash": "0000000000000000000abc..."
}
```

### `GET /api/evidence/{id}/timestamp/rfc3161`

Returns RFC 3161 timestamp status from the configured TSA (FreeTSA by default):

```json
{
  "evidence_id": 1,
  "sha256": "abcd...",
  "timestamped": true,
  "verified": false,
  "error": null
}
```

### `POST /api/evidence/{id}/timestamp/rfc3161`

Create an RFC 3161 timestamp for the evidence hash via the configured TSA. Stores
a detached `.tsr` file in `backend/data/timestamps/`. Returns **503** if RFC 3161
is disabled or the TSA does not respond. Logs an `ANNOTATED` custody event.

### `GET /api/evidence/{id}/timestamp/rfc3161/file`

Download the detached `.tsr` file.

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

Optional `role` query param. Links an entity to a piece of evidence and records a `LINKED` custody event.

```bash
curl -X POST "http://127.0.0.1:8000/api/entities/1/link/1?role=named%20party"
```

### `DELETE /api/entities/{entity_id}/link/{evidence_id}`

Removes the evidence link. Returns **204**.

### `GET /api/entities/{entity_id}/evidence`

Returns evidence linked to this entity.

```json
[
  { "id": 1, "title": "PBO Report 2024", "sha256": "abcd...", "role": "named party" }
]
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

### `POST /api/relationships/{relationship_id}/link/{evidence_id}`

Links evidence to a relationship. Returns **201**.

### `DELETE /api/relationships/{relationship_id}/link/{evidence_id}`

Unlinks evidence from a relationship. Returns **204**.

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

### `PATCH /api/timeline/{id}`

Update any subset of `title`, `description`, `occurred_at`, `evidence_id`. Returns updated `TimelineEventRead`.

### `DELETE /api/timeline/{id}`

Returns **204**; **404** if not found.

---

## Collect (`/api/collect`) — Track A

### `POST /api/collect/batch`

Collect multiple public URLs concurrently. Returns per-URL success/failure.

```json
{
  "items": [
    { "url": "https://example.gov/report1.pdf", "collected_by": "operator" },
    { "url": "https://example.gov/report2.pdf", "title": "Report 2", "notes": "..." }
  ]
}
```

Response:

```json
[
  { "url": "https://example.gov/report1.pdf", "success": true, "evidence_id": 1, "sha256": "abcd..." },
  { "url": "https://example.gov/report2.pdf", "success": false, "error": "..." }
]
```

The batch is capped at `VERITAS_COLLECT_BATCH_LIMIT` (default 50).

### `POST /api/collect/crawl`

Fetch a root URL, discover first-level links matching a regex pattern, and collect each one.

```json
{
  "root_url": "https://example.gov/publications/",
  "link_pattern": "\\.pdf$",
  "title_prefix": "Publication:",
  "collected_by": "operator"
}
```

---

## Authentication (`/api/auth`)

### `POST /api/auth/token`

OAuth2-compatible login endpoint. Returns a JWT access token that must be sent
as `Authorization: Bearer <token>` on all write operations.

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Change the default admin password via the `VERITAS_ADMIN_PASSWORD` environment
variable.

---

## Export (`/api/export`)

### `GET /api/export/pubkey`

Return the Ed25519 public key (hex) used to sign vault export bundles. Verifies
the bundle offline without needing Veritas running.

```json
{ "public_key_hex": "a1b2c3...", "algorithm": "Ed25519" }
```

### `POST /api/export/signed-package`

Build a cryptographically signed export bundle. Requires admin JWT. The returned
bundle is a tar.gz archive at `backend/data/veritas-signed-{vault_id}.tar.gz`
containing:

- `manifest.json` — all evidence, entities, relationships, timeline events
- `custody_log.json` — every `ChainOfCustodyEvent` with `prev_hash` chain
- `store/` — raw content-addressed evidence objects
- `timestamps/` — all `.ots` and `.tsr` timestamp receipts
- `PUBKEY` — hex Ed25519 public key
- `SIGNATURE` — detached Ed25519 signature over SHA-256(unsigned_bundle)

```json
{
  "bundle_path": ".../veritas-signed-export.tar.gz",
  "public_key_hex": "a1b2c3...",
  "evidence_count": 12,
  "custody_event_count": 47,
  "storage_bytes": 926952,
  "vault_id": "export"
}
```

### `GET /api/export/signed-package/download`

Download the bundle generated by `POST /api/export/signed-package` for the same
`vault_id`.

### `POST /api/export/verify-bundle`

Upload a signed bundle (multipart `file`). Returns whether the signature is valid
and the signing public key embedded inside it.

```json
{
  "valid": true,
  "error": null,
  "public_key_hex": "a1b2c3...",
  "signed_at": "2026-06-26T...",
  "vault_id": "export",
  "sha256_of_bundle": "..."
}
```

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
