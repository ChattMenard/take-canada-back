# Roadmap

Veritas is built in phases. The architecture for all three phases exists today;
this file tracks what is implemented versus planned.

## Status legend

- ✅ Done
- 🟡 Foundation in place (API/model exists, UI/automation pending)
- ⬜ Planned

## Phase 1 — Evidence Vault 🟡

- ✅ SHA-256 hashing on ingest
- ✅ Content-addressed, deduplicated object store
- ✅ Provenance metadata (source URL, capture date, collector, notes)
- ✅ API-only custody log
- ✅ Integrity verification (re-hash + compare), logged
- ✅ Download/export with audit logging
- ✅ Search, list, stats
- ✅ Full Vault UI
- ✅ OpenTimestamps timestamp anchoring
- ✅ RFC 3161 timestamp anchoring (TSA)
- ✅ Hash-chained custody log
- ✅ Authentication + JWT admin tokens
- ✅ Commercial RFC 3161 TSA support (DigiCert/Sectigo)
- ✅ Rendered screenshot / HTML snapshot at collection time (Playwright path)
- ✅ HTTP response header capture at collection time
- ✅ C2PA manifest generation (unsigned by default; certificate signing optional)
- 🟡 PostgreSQL backend (env-switchable; RLS policies defined, not applied by default)
- ✅ Signed exports (Ed25519-signed bundle: manifest + custody log + objects + timestamp receipts)

## Phase 2 — Entity & Relationship Graph 🟡

- ✅ `Entity` model + CRUD API
- ✅ `Relationship` model + CRUD API
- ✅ Evidence ↔ entity / relationship link tables + linking API
- ✅ Entity management UI
- ✅ Relationship list + linked-evidence UI
- ⬜ Graph visualization (interactive network diagram)
- ⬜ "Attach evidence to a claim" guided UI flow

## Phase 3 — Searchable Archive & Timeline 🟡

- ✅ `TimelineEvent` model + CRUD API
- ✅ Timeline UI (chronological view)
- ✅ Text extraction for PDFs and HTML (via `pdfminer.six` and `BeautifulSoup`)
- ✅ Full-text search across metadata + extracted text (SQLite FTS5)
- ⬜ OCR for scanned images
- ⬜ Search UI highlighting and filters

## Cross-cutting tracks

### Track A — Effortless collection 🟡

- ✅ One-click **URL collector** endpoint (fetch + hash + ingest + provenance) with SSRF guard
- ✅ "From URL" tab in the collect UI
- ✅ Capture HTTP status, content type, final URL, and retrieval time in custody
- ✅ Capture HTTP response headers as a companion file
- ✅ Rendered screenshot / HTML snapshot at collection time (Playwright path)
- ✅ Batch collection (`/api/collect/batch`)
- ✅ Crawl collection (`/api/collect/crawl`)

### Track B — Case-building 🟡

- See Phase 2 & 3 UIs above.

### Track C — Durability & trust 🟡

- ✅ OpenTimestamps timestamp anchoring
- ✅ RFC 3161 timestamp anchoring (TSA)
- ✅ Commercial RFC 3161 TSA support (DigiCert/Sectigo)
- ✅ Append-only **hash chain** linking custody events
- ✅ Authentication + JWT admin tokens
- ✅ C2PA manifest generation (unsigned by default; optional certificate signing)
- ✅ Vault export as a signed archive (Ed25519; verifiable offline)
- 🟡 PostgreSQL backend (env-switchable; RLS policies defined, not applied by default)
- ✅ Automated tests for hashing, storage, custody, verify, entities, relationships, timeline, extractor
- ✅ `docker-compose.yml` + backend/frontend `Dockerfile`s for one-command run

## Guiding priorities

1. **Make collecting cost the operator nothing** (Track A).
2. **Turn evidence into a documented, sourced case** (Phases 2–3).
3. **Make integrity provable to outsiders, not just to ourselves** (Track C).

See [INTEGRITY.md](./INTEGRITY.md) for the rationale behind the hardening items.
