"""Vault seal endpoint.

Once sealed, the evidence vault becomes read-only forever. The seal is enforced
by filesystem permissions (chmod 444) and an in-memory flag that rejects write
operations.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..config import DATA_DIR, settings
from ..routers.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

SEAL_FILE = DATA_DIR / ".sealed"


# Load seal state from file on startup
def _load_seal_state() -> bool:
    if SEAL_FILE.exists():
        return True
    return False


_vault_sealed = _load_seal_state()


class SealStatus(BaseModel):
    sealed: bool
    sealed_at: str | None = None
    evidence_objects: int
    timestamp_files: int
    db_path: str


class SealResult(BaseModel):
    sealed: bool
    sealed_at: str
    evidence_objects_locked: int
    timestamp_files_locked: int
    db_path: str
    db_readonly: bool


def _set_readonly(path: Path) -> bool:
    """Recursively chmod all files under path to 444."""
    changed = 0
    if path.exists():
        for p in path.rglob("*"):
            if p.is_file():
                os.chmod(p, 0o444)
                changed += 1
    return changed


@router.get("/seal", response_model=SealStatus)
def get_seal_status():
    """Return whether the vault is sealed and what would be locked."""
    evidence_count = 0
    if settings.storage_dir.exists():
        evidence_count = sum(1 for p in settings.storage_dir.rglob("*") if p.is_file())
    timestamp_count = 0
    if settings.timestamp_dir.exists():
        timestamp_count = sum(1 for p in settings.timestamp_dir.rglob("*") if p.is_file())
    sealed_at = None
    if _vault_sealed and SEAL_FILE.exists():
        sealed_at = SEAL_FILE.read_text().strip()
    return SealStatus(
        sealed=_vault_sealed,
        sealed_at=sealed_at,
        evidence_objects=evidence_count,
        timestamp_files=timestamp_count,
        db_path=str(DATA_DIR / "veritas.db"),
    )


@router.post("/seal", response_model=SealResult)
def seal_vault(admin: str = Depends(get_current_admin)):
    """Permanently seal the vault.

    Locks every evidence object and timestamp file to 444. Also locks the
    SQLite database file to 444. After this call, all POST/PUT/DELETE write
    endpoints in the app will return 423 Locked until the process is restarted
    (and the DB remains read-only at the filesystem level).
    """
    global _vault_sealed
    if _vault_sealed:
        raise HTTPException(status_code=400, detail="Vault is already sealed.")

    sealed_at = datetime.now(timezone.utc).isoformat()

    db_path = DATA_DIR / "veritas.db"
    evidence_locked = _set_readonly(settings.storage_dir)
    timestamp_locked = _set_readonly(settings.timestamp_dir)

    db_readonly = False
    if db_path.exists():
        os.chmod(db_path, 0o444)
        db_readonly = True

    # Write seal timestamp to file for persistence across restarts
    SEAL_FILE.write_text(sealed_at)

    _vault_sealed = True
    return SealResult(
        sealed=True,
        sealed_at=sealed_at,
        evidence_objects_locked=evidence_locked,
        timestamp_files_locked=timestamp_locked,
        db_path=str(db_path),
        db_readonly=db_readonly,
    )


def is_vault_sealed() -> bool:
    return _vault_sealed


def ensure_unsealed():
    """Call from any write endpoint; raises 423 if sealed."""
    if _vault_sealed:
        raise HTTPException(
            status_code=423,
            detail="Vault is sealed. No new evidence can be added.",
        )
