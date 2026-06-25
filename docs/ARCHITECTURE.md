# Architecture

Veritas is a two-tier application: a **Python engine** that owns all integrity
and persistence concerns, and a **React UI** that is a thin client over the
engine's HTTP API. Everything important happens in the backend; the frontend
holds no authoritative state.

## High-level diagram

```text
        ┌─────────────────────────────────────────────┐
        │                  Browser                     │
        │   React + Vite + Tailwind (frontend/)        │
        │   - Vault UI, ingest form, custody timeline  │
        └───────────────┬─────────────────────────────┘
                        │  HTTP (JSON + multipart)
                        │  dev: Vite proxies /api → :8000
        ┌───────────────▼─────────────────────────────┐
        │              FastAPI app (backend/)          │
        │  routers: evidence | collect | entities |     │
        │           relationships | timeline | meta     │
        └───────┬───────────────────────┬──────────────┘
                │                        │
        ┌───────▼────────┐      ┌────────▼─────────────┐
        │  SQLite (DB)   │      │  Content-addressed   │
        │  veritas.db    │      │  object store        │
        │  metadata,     │      │  data/store/<ab>/<h> │
        │  custody log   │      │  raw bytes by SHA-256│
        └────────────────┘      └──────────────────────┘
```

## Why this split

- **The engine is the source of truth.** Hashing, storage, and the custody log
  must never depend on a client behaving correctly. A malicious or buggy UI
  cannot forge integrity.
- **The store and the database are separable.** Metadata (small, queryable)
  lives in SQLite; raw bytes (large, immutable) live on disk addressed by hash.
  You can back up, mirror, or move either independently.
- **Content addressing gives integrity for free.** Because a file's location is
  derived from its hash, you cannot silently swap its contents — the path would
  no longer match.

## Backend modules

| Module | Responsibility |
| --- | --- |
| `app/main.py` | Builds the FastAPI app, configures CORS, mounts routers, exposes `/api/health` and `/api/stats`, creates tables on startup. |
| `app/config.py` | `Settings` (env-overridable): app name, DB URL, storage dir, CORS origins, max upload size. Creates data dirs on import. |
| `app/database.py` | SQLModel engine, `init_db()` (create tables), `get_session()` dependency. |
| `app/storage.py` | The object store: `hash_bytes`, `hash_file`, `store_bytes`, `verify`, `get_path`, `disk_usage_bytes`. |
| `app/models.py` | All ORM tables across the three phases + enums. |
| `app/schemas.py` | Pydantic DTOs kept separate from ORM tables for clean request/response contracts. |
| `app/routers/evidence.py` | The vault: ingest, URL collect, list, get, patch metadata, note, verify, download. |
| `app/routers/entities.py` | Phase 2 foundation: entity CRUD + evidence linking. |
| `app/routers/relationships.py` | Phase 2 foundation: relationship CRUD + evidence linking. |
| `app/routers/timeline.py` | Phase 3 foundation: timeline event CRUD. |
| `app/routers/collect.py` | Batch and crawl URL collection. |

## Request lifecycle: ingesting evidence

1. `POST /api/evidence` arrives as `multipart/form-data` (file + metadata).
2. The router reads the bytes and enforces the size limit.
3. `storage.store_bytes()` computes the SHA-256 and writes the bytes to
   `data/store/<first2>/<full-hash>` **only if not already present** (idempotent,
   deduplicated). Writes go to a temp file then atomically rename.
4. An `Evidence` row is inserted with the hash + provenance metadata.
5. A `ChainOfCustodyEvent` of action `CREATED` is appended, stamping the hash.
6. The full record (with custody events) is returned.

## Technology choices

- **FastAPI** — typed, async-capable, auto-generated OpenAPI docs at `/docs`.
- **SQLModel** — Pydantic + SQLAlchemy; one model definition for table + types.
- **SQLite** — zero-dependency, file-based, perfect for single-node and easy
  backup. The `database_url` setting allows swapping to Postgres later.
- **React + Vite + Tailwind** — fast dev loop, modern UI, no heavy framework lock-in.
- **lucide-react** — clean, consistent icon set.

## Configuration

All settings are environment-overridable with the `VERITAS_` prefix (see
`app/config.py`). Examples:

```bash
export VERITAS_MAX_UPLOAD_MB=1024
export VERITAS_DATABASE_URL="sqlite:////absolute/path/veritas.db"
```

## Known architectural limits (today)

- **Single user, no authentication.** Intended for local/trusted use right now.
- **No background workers.** Ingest is synchronous within the request.
- **SQLite write concurrency.** Fine for one operator; revisit for multi-writer.

See [ROADMAP.md](./ROADMAP.md) for how these are addressed in later phases.
