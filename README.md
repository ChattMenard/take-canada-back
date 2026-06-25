# Veritas — Open-Source Evidentiary Collection Engine

> ⚠️ **Prototype status.** This is a working proof of concept, not a
> production-ready legal-evidence system. It detects accidental or unprivileged
> tampering via SHA-256 re-verification, but it is **not tamper-proof against
> a privileged attacker** and it does not yet provide cryptographic proof of
> time. See [INTEGRITY.md](./docs/INTEGRITY.md) for the honest limits.

A self-hostable engine for **collecting, preserving, and auditing public-record
evidence**. Every document is hashed with SHA-256 on arrival, stored in a
content-addressed object store, and tracked with a **chain-of-custody log**. A
stored file can be re-verified later to detect accidental or malicious changes.

Built for transparency work and accountability journalism. MIT-licensed and
fully open source by design.

## Status

Phased build. The architecture for all three phases is implemented as a working
foundation; the remaining work is hardening so the system can survive legal and
adversarial scrutiny.

- **Phase 1 — Evidence Vault (foundation):** ingest, SHA-256 hashing, provenance
  metadata, custody log, integrity verification, download/export.
- **Phase 2 — Entity & Relationship Graph (foundation):** API + UI for people,
  banks, agencies, companies and the links between them.
- **Phase 3 — Searchable Archive & Timeline (foundation):** timeline API + UI,
  and full-text search across metadata and extracted document text.

**Implemented hardening:**

- **OpenTimestamps anchoring** — evidence hashes are submitted as a best-effort
  background task on ingest, producing a detached `.ots` signature. Once the
  calendar commitment is included in a Bitcoin block, the signature proves the hash
  existed no later than that block time. The submission can fail silently if the
  calendars are unreachable; verification reports `pending` until a block confirms.
- **RFC 3161 anchoring** — evidence hashes can be submitted to an RFC 3161 trusted
  timestamp authority (FreeTSA by default), producing a detached `.tsr` signature.
  The TSA-signed token proves the hash existed at the signed time, without waiting
  for a blockchain confirmation. See `POST /api/evidence/{id}/timestamp/rfc3161`.

**Remaining hardening:** hash-chained custody log, signed exports, PostgreSQL
concurrency hardening, and authentication/roles.

## Documentation

Full docs live in [`docs/`](./docs/README.md):

- [Architecture](./docs/ARCHITECTURE.md) — how the engine and UI fit together
- [Data Model](./docs/DATA_MODEL.md) — every table and field, and why
- [API Reference](./docs/API.md) — all endpoints with examples
- [Usage Guide](./docs/USAGE.md) — collecting, verifying, exporting evidence
- [Integrity & Custody](./docs/INTEGRITY.md) — guarantees and honest limits
- [Deployment](./docs/DEPLOYMENT.md) — running, configuring, backing up
- [Transparency Campaign](./docs/TRANSPARENCY_CAMPAIGN.md) — citizen ATIP templates for financial accountability
- [Evidence Validation](./docs/EVIDENCE_VALIDATION.md) — fact-checking framework for financial claims
- [Roadmap](./docs/ROADMAP.md) · [Contributing](./docs/CONTRIBUTING.md) · [Security](./docs/SECURITY.md) · [Glossary](./docs/GLOSSARY.md)

## Architecture

```text
backend/   FastAPI + SQLModel (SQLite). The engine: hashing, storage, custody.
frontend/  React + Vite + Tailwind. The Vault UI.
```

Data model (see `backend/app/models.py`):

- `Evidence` + `ChainOfCustodyEvent` — the vault (phase 1)
- `Entity` + `Relationship` — the collusion graph (phase 2)
- `TimelineEvent` — chronology (phase 3)
- link tables connect one source document to many entities/relationships/events

## Running locally

### 1. Backend (port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs at <http://127.0.0.1:8000/docs>

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server proxies `/api` to the backend.

### Docker Compose (one command)

```bash
docker-compose up --build
```

- Backend: <http://localhost:8000>
- Frontend: <http://localhost>

## How integrity checks work

1. On ingest, the raw bytes are hashed with SHA-256. The hash *is* the storage
   path (`data/store/ab/abcd…`), so identical bytes are never duplicated.
2. The hash is recorded on the `Evidence` row and stamped into the first
   custody event (`CREATED`).
3. **Verify** re-reads the stored object, recomputes the digest, and compares.
   The result (`VERIFIED` / `VERIFY_FAILED`) is appended to the custody log.
4. Every access, annotation, export, link, and verification is recorded in the
   custody log. The API does not expose edit or delete for these events.

**What this does not prove.** A party with shell access to both the database and
object store can, in principle, rewrite the file and the hash record. This is
tamper-**detection** for ordinary handling, not tamper-**proofing** against a
compromised server. OpenTimestamps anchoring already provides external proof of
existence once confirmed; a hash-chained log is the next step to make internal
tampering detectable.

## Data location

All data lives under `backend/data/` (the SQLite DB and the object store). Back
up that directory to preserve your evidence. It is git-ignored by default.

## License

MIT — see `LICENSE`. Use it, fork it, mirror it.
