"""Vault export API — generate manifest and package for public release."""

import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ..config import settings
from ..database import get_session
from ..models import ChainOfCustodyEvent, Entity, Evidence, Relationship_, TimelineEvent
from ..routers import seal
from ..routers.seal import ensure_unsealed
from ..routers.auth import get_current_admin
from ..schemas import BundleVerifyResult, ExportResult, ExportSignedResult, Stats, VaultManifest
from ..signed_export import build_signed_bundle, get_public_key_hex, verify_bundle
from ..storage import disk_usage_bytes, verify, verify_all

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/manifest", response_model=VaultManifest)
def generate_manifest(
    vault_id: str = "manual-export",
    session: Session = Depends(get_session),
):
    """Generate a manifest of the entire vault for public release.

    The manifest includes all evidence metadata, entities, relationships,
    and timeline events. It does NOT include the raw file bytes or the
    SQLite database — those are packaged separately.
    """
    evidence = session.exec(select(Evidence)).all()
    entities = session.exec(select(Entity)).all()
    relationships = session.exec(select(Relationship_)).all()
    timeline = session.exec(select(TimelineEvent)).all()

    stats = Stats(
        evidence_count=len(evidence),
        entity_count=len(entities),
        relationship_count=len(relationships),
        timeline_count=len(timeline),
        storage_bytes=disk_usage_bytes(),
    )

    # Get seal status
    seal_status = seal.get_seal_status()
    seal_data = None
    if seal_status.sealed:
        seal_data = {
            "sealed": True,
            "sealed_at": seal_status.sealed_at,
            "evidence_objects": seal_status.evidence_objects,
            "timestamp_files": seal_status.timestamp_files,
        }

    return VaultManifest(
        version="1.0",
        generated_at=datetime.now(timezone.utc),
        vault_id=vault_id,
        seal=seal_data,
        stats=stats,
        evidence=evidence,
        entities=entities,
        relationships=relationships,
        timeline=timeline,
    )


@router.post("/verify-all")
def verify_all_evidence(session: Session = Depends(get_session)):
    """Verify integrity of all evidence in the vault.

    Returns a summary of verification results. Any failures are
    logged to the custody log for each affected item.
    """
    evidence = session.exec(select(Evidence)).all()
    results = verify_all(evidence)

    return {
        "total": len(evidence),
        "verified": sum(1 for r in results if r["intact"]),
        "failed": sum(1 for r in results if not r["intact"]),
        "details": results,
    }


@router.post("/package", response_model=ExportResult)
def package_vault(
    vault_id: str = "manual-export",
    include_store: bool = True,
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session),
):
    """Generate a manifest and optionally package the object store.

    This is a heavy operation. If include_store is True, a tarball
    of the entire object store is created. The manifest is always
    generated and written to the data directory.
    """
    ensure_unsealed()

    # Generate manifest
    manifest = generate_manifest(vault_id, session)

    # Write manifest to data directory
    manifest_path = settings.data_dir / f"veritas-manifest-{vault_id}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)

    package_path = None

    if include_store:
        # Create tarball of object store
        package_path = settings.data_dir / f"veritas-data-{vault_id}.tar.gz"
        store_path = settings.storage_dir
        timestamp_path = settings.timestamp_dir

        with tarfile.open(package_path, "w:gz") as tar:
            if store_path.exists():
                tar.add(store_path, arcname="store")
            if timestamp_path.exists():
                tar.add(timestamp_path, arcname="timestamps")

    return ExportResult(
        manifest_path=str(manifest_path),
        package_path=str(package_path) if package_path else None,
        evidence_count=manifest.stats.evidence_count,
        storage_bytes=manifest.stats.storage_bytes,
    )


@router.get("/pubkey")
def get_signing_pubkey():
    """Return the vault's Ed25519 public key (hex) used to sign export bundles."""
    return {"public_key_hex": get_public_key_hex(), "algorithm": "Ed25519"}


@router.post("/signed-package", response_model=ExportSignedResult)
def signed_package(
    vault_id: str = "export",
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    """Build a signed export bundle.

    The bundle is a tar.gz archive containing the full vault manifest,
    custody log, all evidence objects, and all timestamp receipts (.ots/.tsr).
    A detached Ed25519 signature over SHA-256(unsigned_bundle) is included as
    the SIGNATURE file. The PUBKEY file contains the hex public key for
    offline verification without Veritas.
    """
    evidence = session.exec(select(Evidence)).all()
    custody_events = session.exec(select(ChainOfCustodyEvent)).all()

    manifest_obj = generate_manifest(vault_id, session)
    manifest_dict = manifest_obj.model_dump(mode="json")

    custody_list = [
        {
            "id": e.id,
            "evidence_id": e.evidence_id,
            "action": e.action.value if hasattr(e.action, "value") else e.action,
            "actor": e.actor,
            "detail": e.detail,
            "hash_at_event": e.hash_at_event,
            "prev_hash": e.prev_hash,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in custody_events
    ]

    bundle_bytes, pub_hex = build_signed_bundle(manifest_dict, custody_list, vault_id)

    bundle_path = settings.data_dir / f"veritas-signed-{vault_id}.tar.gz"
    bundle_path.write_bytes(bundle_bytes)

    return ExportSignedResult(
        bundle_path=str(bundle_path),
        public_key_hex=pub_hex,
        evidence_count=len(evidence),
        custody_event_count=len(custody_events),
        storage_bytes=disk_usage_bytes(),
        vault_id=vault_id,
    )


@router.get("/signed-package/download")
def download_signed_package(
    vault_id: str = "export",
    admin: str = Depends(get_current_admin),
):
    """Download the most recently generated signed bundle for vault_id."""
    bundle_path = settings.data_dir / f"veritas-signed-{vault_id}.tar.gz"
    if not bundle_path.exists():
        raise HTTPException(404, "No signed bundle found. Run POST /api/export/signed-package first.")
    return FileResponse(
        bundle_path,
        media_type="application/gzip",
        filename=bundle_path.name,
    )


@router.post("/verify-bundle", response_model=BundleVerifyResult)
async def verify_signed_bundle(file: UploadFile = File(...)):
    """Verify a signed bundle produced by POST /api/export/signed-package.

    Upload the .tar.gz bundle. Returns whether the Ed25519 signature is valid.
    """
    data = await file.read()
    result = verify_bundle(data)
    return BundleVerifyResult(**result)
