# Glossary

**Chain of custody** — An append-only log of every action taken on a piece of
evidence (creation, access, verification, annotation, export), each stamped with
a timestamp and the hash observed at that moment. In TAKE_CANADA_BACK these records
cannot be edited or deleted.

**Content-addressed storage** — A storage scheme where a file's location is
derived from a hash of its contents. In TAKE_CANADA_BACK, files live at
`data/store/<first2>/<sha256>`. Changing the contents changes the address, which
is what makes tampering evident.

**Evidence** — A preserved item (document, PDF, screenshot, record) plus its
provenance metadata and custody history.

**Entity** — A real-world actor tracked in the graph: a person, bank, agency,
company, or other organization.

**Hash / SHA-256** — A 256-bit cryptographic digest of a file's bytes. Any
change to the bytes produces a completely different digest, so it acts as a
tamper-evident fingerprint.

**Idempotent ingest** — Uploading identical bytes twice results in a single
stored object (deduplication by hash), though it may create separate `Evidence`
records pointing at the same object.

**Provenance** — The origin metadata of an item: source URL, source description,
when it was captured/published (`captured_at`), and who collected it.

**Relationship** — A directed link between two entities (donation, contract,
board seat, ownership, lobbying, employment, other), optionally substantiated by
evidence.

**Tamper-evident vs. tamper-proof** — *Tamper-evident* means alterations can be
**detected** (TAKE_CANADA_BACK's current guarantee). *Tamper-proof* means alterations are
**prevented** even against privileged attackers (a roadmap goal via hash-chaining
and external anchoring).

**Timeline event** — A dated event in a chronology, optionally linked to a piece
of supporting evidence.

**Verification** — Re-reading a stored file, recomputing its SHA-256, and
comparing it to the recorded hash to confirm the bytes are unchanged. Each check
is logged to the chain of custody.
