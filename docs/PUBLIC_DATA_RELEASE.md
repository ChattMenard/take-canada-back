# Public Data Release Strategy

## Goal

Make the Veritas vault's evidence collection publicly accessible and verifiable without compromising the integrity of the source database. The public should be able to:
- Browse the evidence catalog
- Download individual documents by hash
- Verify the integrity of the collection
- See the entity/relationship graph and timeline
- Access the data without running the full Veritas stack

## Architecture

### Separation of Concerns

- **Code repository** (`ChattMenard/Veritas`): Source code only. No data.
- **Data repository** (`ChattMenard/Veritas-data`): Exported vault data, versioned by release.
- **Public index**: Static HTML/JS generated from the manifest for browsing.

### Data Layers

1. **Manifest** (`veritas-manifest.json`): Small, version-controllable metadata
2. **Object store** (`data/store/`): Content-addressed files by SHA-256
3. **Timestamps** (`data/timestamps/`): OpenTimestamps `.ots` and RFC 3161 `.tsr` files
4. **Database** (`data/veritas.db`): NOT exported — only the manifest is needed for public access

## Manifest Schema

```json
{
  "version": "1.0",
  "generated_at": "2026-06-25T23:00:00Z",
  "vault_id": "release-2024-06-25",
  "seal": {
    "sealed": true,
    "sealed_at": "2026-06-25T22:00:00Z",
    "opentimestamps_attestation": "https://blockstream.info/tx/...",
    "rfc3161_attestation": "sha256:..."
  },
  "stats": {
    "evidence_count": 100,
    "entity_count": 50,
    "relationship_count": 75,
    "timeline_count": 30,
    "storage_bytes": 123456789
  },
  "evidence": [
    {
      "id": 1,
      "sha256": "abcd...",
      "title": "Example Document",
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size_bytes": 123456,
      "source_url": "https://example.gov/doc.pdf",
      "source_description": "Government publication",
      "captured_at": "2024-01-15T00:00:00Z",
      "collected_by": "operator",
      "notes": "Primary source for X",
      "custody_event_count": 5,
      "timestamped": true,
      "timestamp_verified": true
    }
  ],
  "entities": [
    {
      "id": 1,
      "name": "Bank of Canada",
      "type": "AGENCY",
      "description": "Central bank"
    }
  ],
  "relationships": [
    {
      "id": 1,
      "source_entity_id": 1,
      "target_entity_id": 2,
      "kind": "CONTRACT",
      "amount": 1000000,
      "occurred_at": "2024-03-01T00:00:00Z",
      "description": "Contract for X",
      "linked_evidence_count": 2
    }
  ],
  "timeline": [
    {
      "id": 1,
      "title": "Event Title",
      "occurred_at": "2024-01-01T00:00:00Z",
      "description": "Description",
      "evidence_id": 1
    }
  ]
}
```

## Export Workflow

### Step 1: Verify Integrity

Before export, run verification on all evidence:
- Re-hash every stored object
- Compare to recorded SHA-256
- Log any mismatches
- Fail export if any verification fails

### Step 2: Seal the Vault

- Call `POST /api/admin/seal`
- Verify seal status
- Generate seal manifest with timestamp attestations

### Step 3: Generate Manifest

- Export all evidence metadata (excluding extracted_text to keep size manageable)
- Export entities and relationships
- Export timeline events
- Include seal status and timestamps
- Write to `veritas-manifest.json`

### Step 4: Package Object Store

- Create `data-store.tar.gz` containing:
  - `data/store/` (all evidence objects)
  - `data/timestamps/` (all timestamp files)
- The manifest references these by hash, so the tar can be extracted anywhere
- Generate `veritas-data-<vault_id>.warc.gz` for archival interoperability:
  - one WARC `resource` record per evidence object
  - one paired WARC `metadata` record with Veritas provenance fields

### Step 5: Publish

- Commit manifest to the data repository
- Attach tarball and WARC archive to a GitHub Release (tagged by date/vault_id)
- Generate static HTML index from manifest
- Deploy static index to a public host (GitHub Pages, Cloudflare Pages, etc.)

## Public Access Patterns

### Browse the Catalog

Users visit the static index and can:
- Search/filter evidence by title, source, tags
- View entity/relationship graph
- Browse timeline
- Download individual files

### Verify Integrity

Users can:
- Download the manifest
- Download the object store tarball
- Extract and verify SHA-256 hashes match the manifest
- Check OpenTimestamps attestations against Bitcoin blockchain
- Check RFC 3161 signatures against the TSA

### Programmatic Access

The manifest is machine-readable. Users can:
- Parse the JSON
- Build their own tools on top of the data
- Mirror the object store to IPFS (content-addressed by design)

## Security Considerations

- **No private data**: Only public records and legally distributable documents
- **No authentication**: Public access is read-only
- **Tamper-evidence**: Manifest is timestamped; object store is content-addressed
- **Reproducibility**: Anyone can re-verify the hashes

## Implementation Plan

1. **Backend API**: `POST /api/export/manifest` to generate the manifest
2. **Backend API**: `POST /api/export/package` to create the tarball
3. **Frontend UI**: "Export vault" button in settings
4. **Static generator**: Script to build HTML index from manifest
5. **CI/CD**: Automated export and release on tag

## Storage Options

### Option A: GitHub Releases

- Pros: Free, integrated with repo, versioned
- Cons: 2GB file size limit per file, 100GB per month bandwidth

### Option B: Separate data repository

- Pros: Git history, can use LFS for large files
- Cons: Large clones, not ideal for binary blobs

### Option C: Cloud storage (R2, S3, Backblaze)

- Pros: Scalable, cheap, CDN-friendly
- Cons: External dependency, cost at scale

### Option D: IPFS

- Pros: Content-addressed by design, decentralized, permanent
- Cons: Requires IPFS gateway or pinning service

**Recommended**: Start with GitHub Releases for the tarball + manifest in a separate repo. Migrate to IPFS for long-term permanence.

## Legal Note

Only include documents that are:
- Public government records
- Court decisions (public domain)
- Research reports with permissive licenses
- ATIP responses that can be legally redistributed

Exclude:
- Documents with copyright restrictions
- Private or confidential information
- Third-party proprietary content
