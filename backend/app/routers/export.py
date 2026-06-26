"""Vault export API — generate manifest and package for public release."""

import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select

from ..config import settings
from ..database import get_session
from ..models import Entity, Evidence, Relationship_, TimelineEvent
from ..routers import seal
from ..routers.seal import ensure_unsealed
from ..schemas import ExportResult, Stats, VaultManifest
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
