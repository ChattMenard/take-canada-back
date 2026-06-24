# Veritas — Open-Source Evidentiary Collection Engine

A self-hostable engine for **collecting, preserving, and auditing public-record
evidence** with tamper-evidence built in. Every document is hashed with SHA-256
on arrival, stored in a content-addressed object store, and tracked with a
complete, append-only **chain of custody**. Integrity can be re-verified at any
time.

Built for transparency work and accountability journalism. MIT-licensed and
fully open source by design.

## Status

Phased build. The architecture for all three phases ships today; phase 1 is
fully implemented.

- **Phase 1 — Evidence Vault (DONE):** ingest, SHA-256 hashing, provenance
  metadata, chain-of-custody log, integrity verification, download/export.
- **Phase 2 — Entity & Relationship Graph (foundation):** API + data model for
  people, banks, agencies, companies and the links between them.
- **Phase 3 — Searchable Archive + Timeline (foundation):** API + data model
  for chronological events tied to evidence.

## Architecture

```
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

API docs at http://127.0.0.1:8000/docs

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` to the backend.

## How tamper-evidence works

1. On ingest, the raw bytes are hashed with SHA-256. The hash *is* the storage
   path (`data/store/ab/abcd…`), so identical bytes are never duplicated.
2. The hash is recorded on the `Evidence` row and stamped into the first
   custody event (`CREATED`).
3. **Verify** re-reads the stored object, recomputes the digest, and compares.
   The result (`VERIFIED` / `VERIFY_FAILED`) is appended to the custody log.
4. Every access, annotation, export, and verification is logged immutably.

## Data location

All data lives under `backend/data/` (the SQLite DB and the object store). Back
up that directory to preserve your evidence. It is git-ignored by default.

## License

MIT — see `LICENSE`. Use it, fork it, mirror it.
