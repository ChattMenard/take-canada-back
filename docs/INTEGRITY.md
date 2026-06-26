# Integrity & Chain of Custody

This document explains the guarantees Veritas makes, how they work, and — just
as importantly — what they do **not** prove. Being precise here is what makes
the tool trustworthy.

## What Veritas currently guarantees

1. **Tamper-detection for ordinary handling.** If a stored file is altered after
   ingest, verification will detect it. The recorded SHA-256 will no longer match
   the bytes.
2. **Deduplication by content.** Identical bytes are stored once. Two uploads of
   the same file resolve to the same object.
3. **API-only custody log.** The API does not expose edit or delete for custody
   events. Every create, access, verify, annotation, link, and export is recorded
   with a timestamp and the hash observed at that moment. A party with direct
   database/filesystem access can bypass this restriction.

## How it works

### Content-addressed storage

When bytes are ingested, Veritas computes `SHA-256(bytes)` and stores the file
at:

```text
data/store/<first-2-hex>/<full-64-hex-digest>
```

The **path is derived from the content**. You cannot replace a file's contents
without changing its hash — and therefore its path. A mismatch between the
recorded `sha256` and the bytes at that path is, by definition, tampering or
corruption.

Writes are atomic: bytes are written to a temporary file and then renamed, so a
crash never leaves a half-written object.

### Verification

`POST /api/evidence/{id}/verify` (or the **Verify integrity** button):

1. Reads the recorded `sha256` from the database.
2. Streams the stored object and recomputes its SHA-256.
3. Compares. Equal → intact. Not equal, or file missing → failure.
4. Appends a `VERIFIED` or `VERIFY_FAILED` custody event.

Because verification is logged, you build a **history of integrity checks** over
time, not just a single point-in-time claim.

### Chain of custody

Every meaningful action writes a `ChainOfCustodyEvent`. The API exposes **no
way to edit or delete** these events through normal use, so the log only grows
as long as the application boundary is respected. Each event captures:

- the **action** (`CREATED`, `VERIFIED`, `EXPORTED`, `ANNOTATED`, `LINKED`, …),
- an optional **actor**,
- a human-readable **detail**,
- the **hash observed** at that time,
- a **timestamp**.

This is **not** a cryptographically enforced append-only log. A database
administrator with shell access can alter or delete rows. Hash-chaining and
external anchoring are the next steps to make tampering detectable outside the
server boundary.

## Threat model — what this defends against

| Threat | Defended? | How |
| --- | --- | --- |
| Silent edit of a stored file | ✅ | Hash mismatch on verify |
| File corruption / bit rot | ✅ | Hash mismatch on verify |
| Accidental duplicate uploads | ✅ | Content addressing dedupes |
| Undocumented handling of an item | ✅ (ordinary use) | API-only custody log |

## What this does **NOT** prove (be honest about limits)

- **It does not prove the *content is true*.** It proves the bytes are unchanged
  *since you collected them*. Authenticity of the source is a separate question.
- **It does not prove *when the source was created*.** `captured_at` is operator-
  supplied metadata, not cryptographic proof of original publication time.
- **It does not prove *when the hash was recorded*.** The custody log timestamps
  are server-generated and can be changed by someone with database access.
  External timestamp anchoring is required for that. OpenTimestamps and RFC 3161
  (FreeTSA) are both implemented today.
- **It is not (yet) tamper-*proof* against a privileged attacker.** Someone with
  write access to the database *and* the object store could, in principle,
  recompute a hash and rewrite both. The current design is tamper-**detectable**
  for ordinary handling, not Byzantine-resistant.

## Hardening roadmap

Implemented and planned in [ROADMAP.md](./ROADMAP.md):

- **OpenTimestamps anchoring** *(implemented)* — each evidence hash is submitted
  as a best-effort background task on ingest, producing a detached `.ots` file.
  Once confirmed in a Bitcoin block, the timestamp proves the hash existed no
  later than that block time, independent of the Veritas server. Until a block
  confirms, the timestamp is `pending` and does not yet prove existence time. See
  the `POST /api/evidence/{id}/timestamp` API.
- **RFC 3161 anchoring** *(implemented)* — each evidence hash can be submitted to
  an RFC 3161 trusted timestamp authority (FreeTSA by default), producing a
  detached `.tsr` file. The returned TimeStampToken is signed by the TSA and
  proves the hash existed at the signed time, without waiting for a blockchain
  confirmation. See the `POST /api/evidence/{id}/timestamp/rfc3161` API.
- **Append-only hash chain** — each custody event references the previous
  event's hash, so the log cannot be edited without breaking the chain.
- **External log anchoring** — periodically publish a digest of the custody log
  itself (e.g., to a public timestamped location) so even a privileged rewrite
  is detectable.
- **PostgreSQL backend** *(implemented)* — switch to PostgreSQL via
  `VERITAS_DATABASE_URL`; Row-Level Security policies are auto-applied to
  make the custody log append-only at the database layer.
- **Signed exports** — bundle evidence + custody + a signature for sharing.
- **Source capture** — store HTTP response headers and a rendered screenshot at
  collection time to strengthen provenance.

## Practical guidance

- Verify items on a schedule and before relying on them.
- Keep `backend/data/` backed up and access-controlled.
- Record *why* a document matters in notes while collecting — context decays.
