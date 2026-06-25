# Contributing

Veritas is open source (MIT) and welcomes contributions that strengthen its
core promise: **collecting and preserving public-record evidence with provable
integrity.**

## Principles

1. **Integrity first.** Never weaken hashing, the append-only custody log, or
   verification for convenience. Changes that touch these need extra scrutiny
   and tests.
2. **Evidence over conclusions.** Features should help users *preserve and cite*
   sources, not assert claims the data doesn't support.
3. **Honest about limits.** Don't overstate guarantees in code, UI, or docs.
   See [INTEGRITY.md](./INTEGRITY.md).
4. **Lawful and factual.** This is an accountability tool grounded in
   public-record evidence and accurate sourcing.

## Getting set up

See [DEPLOYMENT.md](./DEPLOYMENT.md). In short:

```bash
# backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

# frontend
cd frontend && npm install && npm run dev
```

## Project conventions

- **Backend**: FastAPI + SQLModel. Keep ORM tables in `models.py` and
  request/response DTOs in `schemas.py` — don't return ORM objects with lazy
  relationships directly except where a read schema covers them.
- **Custody logging**: any new action that handles evidence should append a
  `ChainOfCustodyEvent`. Never add an edit/delete path for custody events.
- **Frontend**: React function components, Tailwind utility classes, icons from
  `lucide-react`. Keep API calls in `src/api.js`.
- **Comments**: write self-explanatory code; add comments only where intent is
  non-obvious.

## Branch & commit

- Branch from `master`: `feature/...`, `fix/...`, `docs/...`.
- Write clear, imperative commit messages (e.g., "Add URL collector endpoint").
- Keep PRs focused; one concern per PR.

## Tests

The backend test suite lives in `backend/tests/` and runs with `pytest`. Contributions
that touch hashing, storage, custody, verify, or model changes should include or
update coverage. Run tests from the `backend/` directory:

```bash
pytest
```

## What's most wanted

See [ROADMAP.md](./ROADMAP.md). High-leverage areas right now:

- Graph visualization for the entity/relationship network
- Guided "attach evidence to a claim" UI flow
- Integrity hardening (hash-chained custody log, signed exports, external anchoring)
- Authentication and multi-user roles for shared deployments

## Reporting issues

Open a GitHub issue with steps to reproduce. For anything security- or
integrity-sensitive, follow [SECURITY.md](./SECURITY.md) instead of filing a
public issue.
