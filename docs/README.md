# Veritas Documentation

Complete documentation for **Veritas**, an open-source, tamper-evident
evidentiary collection engine for public-record accountability work.

> **Mission in one line:** make it easy to *collect, preserve, and prove the
> integrity of* public-record evidence — so findings are credible, sourced,
> and defensible.

## Start here

| If you want to… | Read |
| --- | --- |
| Understand what Veritas is and how the pieces fit | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Know exactly what data is stored and why | [DATA_MODEL.md](./DATA_MODEL.md) |
| Call the API (every endpoint, with examples) | [API.md](./API.md) |
| Collect and verify evidence step by step | [USAGE.md](./USAGE.md) |
| Understand the tamper-evidence guarantees | [INTEGRITY.md](./INTEGRITY.md) |
| Run or self-host it | [DEPLOYMENT.md](./DEPLOYMENT.md) |
| Contribute code | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| Report a vulnerability | [SECURITY.md](./SECURITY.md) |
| See what's built and what's next | [ROADMAP.md](./ROADMAP.md) |
| Look up a term | [GLOSSARY.md](./GLOSSARY.md) |

## The 60-second mental model

1. You **collect** a document (upload, or fetch from a public URL).
2. On arrival it is **hashed with SHA-256**. That hash is its permanent fingerprint.
3. The bytes are saved in a **content-addressed store** (the file's path *is* its hash).
4. Veritas records **provenance** (where it came from, when, who collected it).
5. Every action is written to an **append-only chain of custody**.
6. At any time, **verification** re-reads the bytes and recomputes the hash to
   prove the evidence has not been altered.

## Project layout

```text
Veritas/
├── backend/            FastAPI + SQLModel (SQLite or PostgreSQL). The engine.
│   ├── app/
│   │   ├── main.py         App entrypoint, CORS, /health, /stats
│   │   ├── config.py       Settings (paths, DB URL, limits)
│   │   ├── database.py     Engine + session + table creation
│   │   ├── storage.py      SHA-256 content-addressed object store
│   │   ├── models.py       All DB tables (3 phases)
│   │   ├── schemas.py      Request/response DTOs
│   │   ├── fetcher.py      Server-side URL fetcher with SSRF guard
│   │   ├── extractor.py    PDF/HTML/text extraction for search
│   │   └── routers/        evidence, collect, entities, relationships, timeline
│   └── tests/          pytest suite for the API and storage
├── frontend/           React + Vite + Tailwind. The Vault UI.
│   └── src/
│       ├── App.jsx         Layout, sidebar, search, stats
│       ├── api.js          API client
│       ├── lib/format.js   Formatting helpers
│       └── components/     IngestForm, EvidenceDetail, EntitiesView, RelationshipsView, TimelineView
└── docs/               You are here.
```

## License

MIT. Use it, fork it, mirror it. See [`../LICENSE`](../LICENSE).
