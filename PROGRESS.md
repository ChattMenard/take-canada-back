# TAKE_CANADA_BACK — Progress Tracker

**Last updated:** 2026-06-30

---

## DONE

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Deploy backend to Railway (FastAPI + SQLite) | ✅ DONE | Live at backend-production-cf1f.up.railway.app, 53 evidence items |
| 2 | Deploy frontend to Netlify (React + Vite) | ✅ DONE | Live at govtbs.netlify.app |
| 3 | Configure environment variables for production | ✅ DONE | CORS locked to production domains |
| 4 | Wire API proxy (Netlify → Railway) | ✅ DONE | /api/* redirects to Railway backend |
| 5 | Test evidence collection workflow end-to-end | ✅ DONE | Verified /api/stats returns 53 items through Netlify |
| 6 | Create production deployment documentation | ✅ DONE | docs/PRODUCTION.md |
| 7 | Complete political donations analysis and cross-reference | ✅ DONE | 14 real pharma companies found in 10M Elections Canada records |
| 8 | Draft Competition Act complaint against IMC | ✅ DONE | EVIDENCE_COLLECTED/ACTION_Competition_Act_Complaint_Filing.md |

---

## PENDING — NEEDS USER ACTION

| # | Task | Blocker |
|---|------|---------|
| 9 | File Ethics Complaint against Duclos | Needs your name/address/email; you must submit to ethics@parl.gc.ca |
| 10 | Submit ATIP requests to 5 government agencies | Documents ready in ATIP_REQUESTS/; you must email each agency |
| 11 | Contact Sakamoto class action counsel | Needs your personal outreach to Class Action Group |
| 12 | Configure custom domain (proofstacked.com) | You said you added Netlify DNS but want Vercel instead — remove from Netlify, fix Vercel root directory, deploy |

---

## NOT STARTED

| # | Task | Notes |
|---|------|-------|
| 13 | Set up monitoring and error tracking | Sentry or similar; low priority |

---

## DELIVERABLES CREATED TONIGHT

- `EVIDENCE_COLLECTED/ACTION_Competition_Act_Complaint_Filing.md` — Formal filing-ready document
- `EVIDENCE_COLLECTED/PoliticalFinance/pharma_donation_analysis.md` — Verified analysis (14 real pharma companies)
- `docs/PRODUCTION.md` — Deployment documentation
- `.vercelignore` — Excludes large dirs from Vercel upload

---

## CLEANUP PERFORMED

Removed unfounded pre-pandemic mRNA conspiracy claims from:
- `README.md` (Phase 1 section)
- `MISSION_STATEMENT.md` (Phase 1 section + Fuckeries #11 and #15)
- Renumbered remaining fuckeries: 1-10, 11-14

## NEXT STEPS

1. Run git commit/push (lock file may need manual removal: `rm .git/index.lock`)
2. Fix Vercel deploy: set Root Directory to `frontend` in dashboard, run `vercel --prod`
3. File Ethics Complaint (fill in [YOUR NAME] placeholders, email ethics@parl.gc.ca)
4. Send 5 ATIP request emails
5. Contact Sakamoto counsel
