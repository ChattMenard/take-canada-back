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
- ⬜ Hash-chained custody log
- 🟡 PostgreSQL backend (env-switchable; not hardened for concurrent writers)
- ⬜ Signed exports

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
- ⬜ Rendered screenshot / HTML snapshot at collection time
- ✅ Batch collection (`/api/collect/batch`)
- ✅ Crawl collection (`/api/collect/crawl`)

### Track B — Case-building 🟡

- See Phase 2 & 3 UIs above.

### Track C — Durability & trust 🟡

- ✅ OpenTimestamps timestamp anchoring
- ✅ RFC 3161 timestamp anchoring (TSA)
- ⬜ Append-only **hash chain** linking custody events
- 🟡 PostgreSQL backend (env-switchable; not hardened for concurrent writers)
- ⬜ Vault backup/export to a single signed archive
- ⬜ Authentication + multi-user roles (for shared deployments)
- ✅ Automated tests for hashing, storage, custody, verify, entities, relationships, timeline, extractor
- ✅ `Dockerfile` + `docker-compose.yml` for one-command run

## Guiding priorities

1. **Make collecting cost the operator nothing** (Track A).
2. **Turn evidence into a documented, sourced case** (Phases 2–3).
3. **Make integrity provable to outsiders, not just to ourselves** (Track C).

See [INTEGRITY.md](./INTEGRITY.md) for the rationale behind the hardening items.
