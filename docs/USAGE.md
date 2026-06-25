# Usage Guide

How to collect, inspect, verify, and export evidence — both through the UI and
the API.

## Prerequisites

Both servers running (see [DEPLOYMENT.md](./DEPLOYMENT.md)):

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

## 1. Collect evidence (UI)

1. Open the UI and click **Preserve evidence**.
2. Drag a file into the drop zone (or click to browse).
3. Fill in provenance — at minimum a **title** and **source URL**. Add
   **captured at**, **collected by**, and **notes** for stronger records.
4. Click **Preserve & hash**. The file is hashed with SHA-256 and stored, and a
   `CREATED` custody event is logged.

Good provenance habits:

- **Always record the source URL** and the **capture date**.
- Put the *significance* of the document in **notes** while it's fresh.
- Use a consistent **collected by** handle so the custody log is attributable.

## 2. Collect evidence from a public URL (one click)

In the **Preserve evidence** dialog, switch to the **From URL** tab, paste a
public URL, add any metadata, and click **Collect & hash**. Veritas fetches the
resource server-side, hashes it, derives the filename (from the
`Content-Disposition` header when present), and records the source URL, HTTP
status, and retrieval time in the chain of custody.

Or via the API:

```bash
curl -s -X POST http://127.0.0.1:8000/api/evidence/collect-url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.gov/report.pdf","collected_by":"YourHandle","notes":"Why this matters."}'
```

This is how the PBO Fiscal Sustainability Report 2024 is collected. A built-in
SSRF guard refuses non-public hosts (see [INTEGRITY.md](./INTEGRITY.md) and
[SECURITY.md](./SECURITY.md)).

## 3. Inspect evidence

In the UI, click any item in the sidebar to open its detail view:

- **Provenance panel** — SHA-256, size, type, source, dates, collector, notes.
- **Chain of custody** — a timeline of every action taken on the item.

## 4. Verify integrity

Click **Verify integrity** (or `POST /api/evidence/{id}/verify`). Veritas
re-reads the stored bytes, recomputes the hash, and compares it to the recorded
value:

- ✅ **Intact** → a `VERIFIED` event is appended.
- ❌ **Altered/missing** → a `VERIFY_FAILED` event is appended and the UI shows a
  red warning.

Verify periodically and before relying on an item — every check is logged.

## 5. Add custody notes

Use the note box in the detail view to record actions or observations (e.g.,
"shared with counsel", "cross-checked against gazette"). Each note is an
immutable `ANNOTATED` custody event.

## 6. Export / download

Click **Download** (or `GET /api/evidence/{id}/download`). The original file is
returned and an `EXPORTED` event is logged, so exports are part of the audit
trail.

## 7. Search

Use the sidebar search box. It matches **title**, **source description**,
**notes**, and **extracted text** from PDF/HTML/text files. The search uses
SQLite FTS5 under the hood and falls back to metadata matching if there are no
full-text hits.

## 8. Build the entity graph (UI)

Switch to the **Entities** tab to create people, banks, agencies, companies, and
other organizations. Select an entity to see evidence linked to it.

Switch to the **Relationships** tab to connect two entities (donation, contract,
board seat, ownership, lobbying, employment, other). Each relationship can
include an amount, date, and description, and can be linked to supporting
evidence.

## 9. Build a timeline (UI)

Switch to the **Timeline** tab to add dated events. Each event can link to a piece
of evidence so the chronology is sourced.

## 10. Batch or crawl collection (API)

For multiple URLs, use the batch collector:

```bash
curl -s -X POST http://127.0.0.1:8000/api/collect/batch \
  -H "Content-Type: application/json" \
  -d '{"items":[{"url":"https://example.gov/a.pdf"},{"url":"https://example.gov/b.pdf"}]}'
```

To crawl a page and collect matching first-level links:

```bash
curl -s -X POST http://127.0.0.1:8000/api/collect/crawl \
  -H "Content-Type: application/json" \
  -d '{"root_url":"https://example.gov/publications/","link_pattern":"\\.pdf$"}'
```

## Tips for building a credible record

- **Preserve originals, not summaries.** Collect the source PDF/page itself.
- **One claim, many sources.** Stronger conclusions cite multiple documents.
- **Never alter stored files.** If you annotate, do it in notes/custody, not the
  bytes — that's what keeps verification meaningful.
- **Back up `backend/data/`.** That directory *is* your evidence.
