"""Vault export API — generate manifest and package for public release."""

import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..config import settings
from ..database import get_session
from ..models import Entity, Evidence, Relationship_, TimelineEvent
from ..routers import seal
from ..schemas import ExportResult, Stats, VaultManifest, WarcExportResult
from ..signed_export import get_public_key, sign_bundle, verify_bundle, create_signed_bundle_from_files
from ..storage import disk_usage_bytes, verify_all
from ..warc import write_warc

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
    include_warc: bool = False,
    session: Session = Depends(get_session),
):
    """Generate a manifest and optionally package the object store.

    This is a heavy operation. If include_store is True, a tarball
    of the entire object store is created. The manifest is always
    generated and written to the data directory.
    """
    # Generate manifest
    manifest = generate_manifest(vault_id, session)

    # Write manifest to data directory
    manifest_path = settings.data_dir / f"veritas-manifest-{vault_id}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)

    package_path = None
    warc_path = None

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

    if include_warc:
        evidence = session.exec(select(Evidence).order_by(Evidence.id)).all()
        warc_path = settings.data_dir / f"veritas-data-{vault_id}.warc.gz"
        _write_warc_or_410(warc_path, evidence, vault_id)

    return ExportResult(
        manifest_path=str(manifest_path),
        package_path=str(package_path) if package_path else None,
        warc_path=str(warc_path) if warc_path else None,
        evidence_count=manifest.stats.evidence_count,
        storage_bytes=manifest.stats.storage_bytes,
    )


@router.post("/warc", response_model=WarcExportResult)
def export_warc(
    vault_id: str = "manual-export",
    session: Session = Depends(get_session),
):
    """Export stored evidence objects as a compressed WARC 1.1 archive."""
    evidence = session.exec(select(Evidence).order_by(Evidence.id)).all()
    warc_path = settings.data_dir / f"veritas-data-{vault_id}.warc.gz"
    _write_warc_or_410(warc_path, evidence, vault_id)
    return WarcExportResult(
        warc_path=str(warc_path),
        evidence_count=len(evidence),
        storage_bytes=disk_usage_bytes(),
        warc_bytes=warc_path.stat().st_size,
    )


def _write_warc_or_410(path: Path, evidence: list[Evidence], vault_id: str) -> None:
    try:
        write_warc(path, evidence, vault_id=vault_id)
    except FileNotFoundError as exc:
        raise HTTPException(410, str(exc)) from exc


@router.get("/pubkey")
def get_public_key_endpoint():
    """Get the Ed25519 public key for verifying signed exports."""
    return {
        "public_key": get_public_key(),
        "algorithm": "Ed25519",
        "format": "PEM"
    }


@router.post("/signed")
def create_signed_export(
    vault_id: str = "manual-export",
    include_store: bool = True,
    include_warc: bool = False,
    session: Session = Depends(get_session),
):
    """Create a cryptographically signed export bundle.
    
    Returns a signed bundle containing the manifest and optionally the
    object store and/or WARC archive. The bundle can be verified offline
    using the public key from /api/export/pubkey.
    """
    # Generate manifest
    manifest = generate_manifest(vault_id, session)
    
    # Write manifest to data directory
    manifest_path = settings.data_dir / f"veritas-manifest-{vault_id}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)
    
    # Create bundle data
    bundle_files = [manifest_path]
    bundle_path = None
    
    if include_store:
        # Create tarball of object store
        bundle_path = settings.data_dir / f"veritas-data-{vault_id}.tar.gz"
        store_path = settings.storage_dir
        timestamp_path = settings.timestamp_dir
        
        with tarfile.open(bundle_path, "w:gz") as tar:
            if store_path.exists():
                tar.add(store_path, arcname="store")
            if timestamp_path.exists():
                tar.add(timestamp_path, arcname="timestamps")
        bundle_files.append(bundle_path)
    
    if include_warc:
        evidence = session.exec(select(Evidence).order_by(Evidence.id)).all()
        warc_path = settings.data_dir / f"veritas-data-{vault_id}.warc.gz"
        _write_warc_or_410(warc_path, evidence, vault_id)
        bundle_files.append(warc_path)
    
    # Create final bundle if we have multiple files
    if len(bundle_files) > 1:
        final_bundle_path = settings.data_dir / f"veritas-bundle-{vault_id}.tar.gz"
        with tarfile.open(final_bundle_path, "w:gz") as tar:
            for file_path in bundle_files:
                tar.add(file_path, arcname=file_path.name)
        bundle_data_path = final_bundle_path
    else:
        bundle_data_path = bundle_files[0]
    
    # Read bundle data and sign it
    with open(bundle_data_path, "rb") as f:
        bundle_data = f.read()
    
    signed_bundle = sign_bundle(manifest.model_dump(mode="json"), bundle_data)
    
    # Write signed bundle
    signed_bundle_path = settings.data_dir / f"veritas-signed-{vault_id}.json"
    with open(signed_bundle_path, "w") as f:
        json.dump(signed_bundle, f, indent=2)
    
    return {
        "signed_bundle_path": str(signed_bundle_path),
        "bundle_path": str(bundle_data_path) if bundle_data_path else None,
        "manifest_path": str(manifest_path),
        "vault_id": vault_id,
        "evidence_count": manifest.stats.evidence_count,
        "storage_bytes": manifest.stats.storage_bytes
    }
