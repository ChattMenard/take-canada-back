# Deployment & Running

Veritas runs as two processes: the **backend** (FastAPI on port 8000) and the
**frontend** (Vite dev server on port 5173). For local accountability work,
running both on your own machine is the recommended setup.

## Requirements

- Python 3.11+
- Node.js 18+ and npm

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- On first run, `data/veritas.db` and `data/store/` are created automatically.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

- UI: `http://localhost:5173`
- The Vite dev server proxies `/api` to `http://127.0.0.1:8000`
  (see `frontend/vite.config.js`), so no CORS config is needed in dev.

## Configuration

Override any setting with a `VERITAS_`-prefixed environment variable
(see `backend/app/config.py`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `VERITAS_DATABASE_URL` | `sqlite:///…/data/veritas.db` | DB location / engine. |
| `VERITAS_STORAGE_DIR` | `…/data/store` | Object store path. |
| `VERITAS_MAX_UPLOAD_MB` | `512` | Max upload size. |
| `VERITAS_CORS_ORIGINS` | localhost:5173 | Allowed browser origins. |

A `.env` file in `backend/` is also read.

## Production build (frontend)

```bash
cd frontend
npm run build      # outputs static files to dist/
npm run preview    # serve the build locally to test
```

Serve `frontend/dist/` from any static host or reverse proxy, and run the
backend behind the same proxy so `/api` reaches port 8000.

## Backups — read this

**`backend/data/` is your evidence.** It contains the SQLite database (metadata
and custody log) plus the object store (the raw files). It is intentionally
git-ignored. Back it up regularly:

```bash
# Simple, consistent snapshot
tar czf veritas-backup-$(date +%F).tgz -C backend data
```

Store backups securely and off-machine. Losing this directory means losing the
vault.

## Security notes for any shared deployment

- There is **no authentication yet** — do not expose the backend to the open
  internet as-is. Put it behind a VPN, SSH tunnel, or an authenticating reverse
  proxy.
- Restrict filesystem permissions on `backend/data/`.
- See [SECURITY.md](./SECURITY.md) and [INTEGRITY.md](./INTEGRITY.md).

## Cloud deployment

The project is deployed with a split stack:

- **Frontend** → Vercel (static, auto-deploy from GitHub `main` branch)
- **Backend** → Railway (containerized, persistent volume)

**Live URLs:**
- **Frontend:** https://proofstacked.com
- **Backend API:** https://backend-production-cf1f.up.railway.app
- **API Docs:** https://backend-production-cf1f.up.railway.app/docs

**Status:** ✅ Fully operational (deployed 2026-06-24)

### Railway backend

The FastAPI backend runs as a Dockerized service on Railway with a persistent
volume mounted at `/app/data` for the SQLite database and object store.

| Setting | Value |
| --- | --- |
| Railway project | `veritas` |
| Service | `backend` |
| Environment | `production` |
| Region | `us-west2` |
| Public URL | `https://backend-production-cf1f.up.railway.app` |
| Volume mount | `/app/data` (5 GB) |
| `VERITAS_DATABASE_URL` | `sqlite:////app/data/veritas.db` |
| `VERITAS_STORAGE_DIR` | `/app/data/store` |
| `VERITAS_CORS_ORIGINS` | `["https://frontend-rho-six-94.vercel.app","http://localhost:5173","http://127.0.0.1:5173"]` |

Deploy the backend from the `backend/` directory:

```bash
railway up --detach
```

### Vercel frontend

The Vite-built frontend is deployed to Vercel, auto-deploying from the
`ChattMenard/take-canada-back` GitHub repo on push to `main`.

| Setting | Value |
| --- | --- |
| Vercel project | `frontend` |
| Production URL | `https://frontend-rho-six-94.vercel.app` |
| `VITE_API_BASE_URL` | `https://backend-production-cf1f.up.railway.app/api` |

Redeploy the frontend from the `frontend/` directory:

```bash
vercel --prod --yes
```

> **Note:** `VITE_API_BASE_URL` is a build-time variable. After changing it,
> redeploy the frontend for the change to take effect.

### Connecting Railway CLI

```bash
railway login                    # one-time auth
cd backend
railway link                     # select project "veritas", env "production", service "backend"
railway up --detach              # deploy
railway logs                     # view deploy logs
railway variables                # inspect env vars
```

## Monitoring & Health Checks

### Health endpoints

- **Backend health:** `GET /api/health` → `{"status":"ok","version":"0.1.0"}`
- **Backend stats:** `GET /api/stats` → evidence/entity counts and storage usage
- **Frontend:** HTTP 200 response with `<title>Veritas — Evidentiary Collection Engine</title>`

### Monitoring commands

```bash
# Backend health check
curl -s https://backend-production-cf1f.up.railway.app/api/health

# Backend statistics
curl -s https://backend-production-cf1f.up.railway.app/api/stats

# Frontend availability
curl -s -I https://proofstacked.com | grep "HTTP"

# Railway logs (last 100 lines)
railway logs --limit 100

# Vercel deployment status
vercel list --prod
```

### Deployment verification checklist

- [ ] Frontend loads at https://proofstacked.com
- [ ] Backend responds at https://backend-production-cf1f.up.railway.app/api/health
- [ ] API docs accessible at https://backend-production-cf1f.up.railway.app/docs
- [ ] CORS allows frontend domain (check browser dev tools)
- [ ] Git push to `main` triggers Vercel redeploy
- [ ] Railway volume persists data across deployments

## Reproducible runs (planned)

A `Dockerfile` + `docker-compose.yml` for one-command startup is on the
[roadmap](./ROADMAP.md) (Track C).
