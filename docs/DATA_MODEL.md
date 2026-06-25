# Data Model

All tables are defined in `backend/app/models.py`. The schema spans three
phases. Phase 1 (evidence + custody) is fully used today; phases 2 and 3 are
implemented with both API and UI.

## Entity-relationship overview

```text
   Evidence 1───* ChainOfCustodyEvent
      │  *                                  (append-only audit log)
      │  └───* TimelineEvent  (optional evidence_id)
      │
      ├──*  EvidenceEntityLink  *──┐
      │                            ▼
      │                          Entity *───┐
      │                                     │ source / target
      └──*  EvidenceRelationshipLink *──► Relationship
```

## Phase 1 — the vault

### `Evidence`

The canonical record for one preserved item.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int (PK) | |
| `sha256` | str (indexed) | Integrity anchor; matches the stored object's path. |
| `title` | str (indexed) | Human label; defaults to filename/hash if omitted. |
| `filename` | str | Original filename. |
| `content_type` | str | MIME type, default `application/octet-stream`. |
| `size_bytes` | int | Size of stored bytes. |
| `source_url` | str? (indexed) | Where it came from. |
| `source_description` | str? | Free-text origin description. |
| `captured_at` | datetime? | When the source material was originally captured/published. |
| `collected_by` | str? | Operator/handle who collected it. |
| `notes` | str? | Context, significance. |
| `extracted_text` | str? | Plain text extracted from PDF/HTML/text for full-text search. |
| `created_at` | datetime (indexed) | When ingested into Veritas. |

### Full-text search (`evidence_fts`)

SQLite FTS5 virtual table synced to the `evidence` table via triggers. Indexes `title`, `source_description`, `notes`, and `extracted_text`. The `GET /api/evidence?q=...` endpoint uses FTS5 first and falls back to `ILIKE` if there are no matches.

### `ChainOfCustodyEvent`

An **append-only** log entry. Records are added, never edited or deleted (the
API exposes no update/delete for custody events by design).

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int (PK) | |
| `evidence_id` | int (FK → evidence) | |
| `action` | enum `CustodyAction` | See below. |
| `actor` | str? | Who performed the action. |
| `detail` | str? | Human-readable description. |
| `hash_at_event` | str? | Digest observed at event time. |
| `timestamp` | datetime (indexed) | |

**`CustodyAction`** values:
`CREATED`, `ACCESSED`, `VERIFIED`, `VERIFY_FAILED`, `EXPORTED`, `ANNOTATED`, `LINKED`.

## Phase 2 — the graph (foundation)

### `Entity`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int (PK) | |
| `name` | str (indexed) | |
| `type` | enum `EntityType` | `PERSON`, `BANK`, `AGENCY`, `COMPANY`, `OTHER`. |
| `description` | str? | |
| `created_at` | datetime | |

### `Relationship` (table name: `relationship`)

A directed link between two entities, optionally substantiated by evidence.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int (PK) | |
| `source_entity_id` | int (FK → entity) | |
| `target_entity_id` | int (FK → entity) | |
| `kind` | enum `RelationshipKind` | `DONATION`, `CONTRACT`, `BOARD_SEAT`, `OWNERSHIP`, `LOBBYING`, `EMPLOYMENT`, `OTHER`. |
| `description` | str? | |
| `amount` | float? | Monetary value, if applicable. |
| `occurred_at` | datetime? | |
| `created_at` | datetime | |

## Phase 3 — the timeline (foundation)

### `TimelineEvent`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int (PK) | |
| `title` | str (indexed) | |
| `description` | str? | |
| `occurred_at` | datetime (indexed) | |
| `evidence_id` | int? (FK → evidence) | Optional supporting evidence. |
| `created_at` | datetime | |

## Link tables

- **`EvidenceEntityLink`** — `(evidence_id, entity_id)` with optional `role`
  describing how the entity figures in that evidence.
- **`EvidenceRelationshipLink`** — `(evidence_id, relationship_id)` connecting a
  source document to the relationship it substantiates.

This many-to-many design means **one document can support many claims**, and
**one claim can be backed by many documents** — the core of building a
defensible case.

## Design principles

- **Custody is immutable.** No edit/delete path for `ChainOfCustodyEvent`.
- **Hash is the spine.** `Evidence.sha256` is both the integrity anchor and the
  storage address.
- **Evidence is first-class; conclusions are derived.** Entities, relationships,
  and timeline events all point *back* to evidence, never the reverse.
