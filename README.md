# Veritas — Open-Source Evidentiary Collection Engine

> ⚠️ **Production-ready for evidence collection.** This system provides
> tamper-evident storage with PostgreSQL Row-Level Security (RLS), cryptographic
> signing, and comprehensive government accountability tracking. It detects
> accidental or unprivileged tampering via SHA-256 re-verification and provides
> cryptographic proof of integrity. See [INTEGRITY.md](./docs/INTEGRITY.md) for
> security guarantees.

A comprehensive engine for **collecting, preserving, and auditing government
accountability evidence**. Features cryptographic integrity guarantees,
economic oppression tracking, and historical parallels analysis. Every document
is hashed with SHA-256 on arrival, stored in a tamper-evident database, and
tracked with a **chain-of-custody log**.

Built for transparency work, accountability journalism, and citizen oversight of
government power. MIT-licensed and fully open source by design.

## Status

**Production-ready with comprehensive government accountability tracking.**

### Completed Features ✅

**Core Evidence System:**

- SHA-256 hashing and tamper-evident storage
- Chain-of-custody logging with PostgreSQL RLS
- Cryptographic Ed25519 signed exports
- WARC 1.1 archival format
- JWT authentication and role-based access

**Economic Evidence System:**

- Small business destruction tracking (2022-2024 scenario analysis)
- Wealth gap policy impact analysis
- Government hypocrisy documentation
- Inflation tax evidence collection
- Wealth transfer mechanism tracking
- Corporate tax structure analysis and revenue impact
- Federal deficit tracking and policy implications

**Historical Parallels Analysis:**

- Nazi Germany legal framework comparisons
- Soviet Union surveillance parallels
- Apartheid South Africa segregation mechanisms
- Early warning signs of authoritarianism

**Transparency Campaign (5 tracks):**

- **Emergency Powers** - Emergencies Act 2022, interim orders, Charter suspensions
- **Surveillance Infrastructure** - CSE, FINTRAC, Bills C-22/C-26 data collection
- **Financial Transparency** - Bank of Canada operations, QE, banking concentration
- **Economic Accountability** - Corporate tax analysis, deficit tracking, fuel sovereignty
- **Civil Liberties Litigation** - CCLA, BCCLA, Citizen Lab challenges

**Deployment:**

- Railway backend: <https://backend-production-cf1f.up.railway.app>
- Vercel frontend: <https://proofstacked.com>
- PostgreSQL with Row-Level Security
- Cryptographic evidence verification

### Remaining Features 🔄

- Multi-user roles beyond single admin
- Advanced search and filtering
- Real-time notifications
- Mobile-responsive interface improvements

## Documentation

Full docs live in [`docs/`](./docs/README.md):

- [Project Structure](./docs/PROJECT_STRUCTURE.md) — complete architecture overview
- [Architecture](./docs/ARCHITECTURE.md) — system design and components
- [API Reference](./docs/API.md) — all endpoints with examples
- [Usage Guide](./docs/USAGE.md) — collecting, verifying, exporting evidence
- [Integrity & Custody](./docs/INTEGRITY.md) — guarantees and security model
- [Security](./docs/SECURITY.md) — security considerations and best practices
- [Transparency Campaign](./docs/TRANSPARENCY_CAMPAIGN.md) — government accountability framework
- [Roadmap](./docs/ROADMAP.md) — development roadmap and future features
- [Glossary](./docs/GLOSSARY.md) — terminology and definitions
- [Peer Mode](./docs/PEER_MODE.md) — collaborative operating framework

## Architecture

```text
backend/   FastAPI + SQLModel (PostgreSQL + RLS). The engine: hashing, storage, custody.
frontend/  React + Vite + Tailwind. Economic evidence dashboard and UI.
```

**Live Deployment:**

- **Backend**: <https://backend-production-cf1f.up.railway.app> (PostgreSQL with RLS)
- **Frontend**: <https://proofstacked.com> (Vercel with API proxy)

**Data Model** (see `backend/app/models.py`):

**Core Evidence:**

- `Evidence` + `ChainOfCustodyEvent` — tamper-evident vault
- `Entity` + `Relationship` — collusion graph
- `TimelineEvent` — chronology tracking

**Economic Evidence:**

- `EconomicIndicator` — wealth gap and business metrics
- `BusinessMetrics` — small business destruction tracking
- `PolicyAction` — government policy impacts
- `HypocrisyTracker` — statements vs. harmful actions
- `WealthTransfer` — wealth transfer mechanisms

**Transparency Campaign:**

- `EmergencyPower` — emergency powers usage
- `SurveillanceInfrastructure` — surveillance programs
- `FinancialTransparency` — financial system tracking
- `CivilLibertiesLitigation` — legal challenges
- `CharterViolation` — rights violations

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

**Production:** PostgreSQL database with Row-Level Security policies and persistent volume storage on Railway.

**Development:** Local PostgreSQL or SQLite under `backend/data/` (git-ignored by default).

**Backup:** Export signed bundles via `/api/export/signed` for cryptographically verifiable backups.

## License

MIT — see `LICENSE`. Use it, fork it, mirror it.
