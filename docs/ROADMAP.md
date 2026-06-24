# Roadmap

Veritas is built in phases. The architecture for all three phases exists today;
this file tracks what is implemented versus planned.

## Status legend

- ✅ Done
- 🟡 Foundation in place (API/model exists, UI/automation pending)
- ⬜ Planned

## Phase 1 — Evidence Vault ✅

- ✅ SHA-256 hashing on ingest
- ✅ Content-addressed, deduplicated object store
- ✅ Provenance metadata (source URL, capture date, collector, notes)
- ✅ Append-only chain of custody
- ✅ Integrity verification (re-hash + compare), logged
- ✅ Download/export with audit logging
- ✅ Search, list, stats
- ✅ Full Vault UI

## Phase 2 — Entity & Relationship Graph 🟡

- 🟡 `Entity` model + CRUD API
- 🟡 `Relationship` model + CRUD API
- 🟡 Evidence ↔ entity / relationship link tables + linking API
- ⬜ Entity management UI
- ⬜ Relationship/graph visualization
- ⬜ "Attach evidence to a claim" UI flow

## Phase 3 — Searchable Archive & Timeline 🟡

- 🟡 `TimelineEvent` model + CRUD API
- ⬜ Timeline UI (chronological view)
- ⬜ Full-text search across document *contents* (not just metadata)
- ⬜ Text extraction / OCR for PDFs and images

## Cross-cutting tracks

### Track A — Effortless collection 🟡

- ✅ One-click **URL collector** endpoint (fetch + hash + ingest + provenance) with SSRF guard
- ✅ "From URL" tab in the collect UI
- ✅ Capture HTTP status, content type, final URL, and retrieval time in custody
- ⬜ Rendered screenshot / HTML snapshot at collection time
- ⬜ Batch collection (e.g., pull many reports from a publication index)

### Track B — Case-building 🟡

- See Phase 2 & 3 UIs above.

### Track C — Durability & trust ⬜

- ⬜ Vault backup/export to a single signed archive
- ⬜ Automated tests for hashing, storage, custody, verify
- ⬜ `Dockerfile` + `docker-compose.yml` for one-command run
- ⬜ Append-only **hash chain** linking custody events
- ⬜ External anchoring of the custody-log digest
- ⬜ Authentication + multi-user roles (for shared deployments)

## Guiding priorities

1. **Make collecting cost the operator nothing** (Track A).
2. **Turn evidence into a documented, sourced case** (Phases 2–3).
3. **Make integrity provable to outsiders, not just to ourselves** (Track C).

See [INTEGRITY.md](./INTEGRITY.md) for the rationale behind the hardening items.
