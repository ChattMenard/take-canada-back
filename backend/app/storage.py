"""Content-addressed, tamper-evident object store.

Files are stored by their SHA-256 digest. Because the path *is* the hash,
the same bytes are never duplicated and integrity can be re-verified at any
time by re-reading the file and recomputing its digest.
"""

import hashlib
import os
import shutil
from pathlib import Path

from .config import settings

CHUNK = 1024 * 1024  # 1 MiB


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object_path(sha256: str) -> Path:
    return settings.storage_dir / sha256[:2] / sha256


def store_bytes(data: bytes) -> tuple[str, Path, int]:
    """Persist bytes and return (sha256, path, size). Idempotent."""
    sha256 = hash_bytes(data)
    dest = _object_path(sha256)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        # Write to a temp file then atomically rename to avoid partial objects.
        tmp = dest.with_suffix(".tmp")
        tmp.write_bytes(data)
        tmp.replace(dest)
        # Lock the evidence object read-only immediately (immutable object).
        os.chmod(dest, 0o444)
    return sha256, dest, len(data)


def get_path(sha256: str) -> Path:
    return _object_path(sha256)


def exists(sha256: str) -> bool:
    return _object_path(sha256).exists()


def verify(sha256: str) -> bool:
    """Re-read the stored object and confirm its digest is unchanged."""
    path = _object_path(sha256)
    if not path.exists():
        return False
    return hash_file(path) == sha256


def delete_object(sha256: str) -> None:
    path = _object_path(sha256)
    if path.exists():
        path.unlink()


def disk_usage_bytes() -> int:
    total = 0
    for p in settings.storage_dir.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def verify_all(evidence_list) -> list[dict]:
    """Verify all evidence items and return results."""
    results = []
    for ev in evidence_list:
        intact = verify(ev.sha256)
        results.append({
            "evidence_id": ev.id,
            "sha256": ev.sha256,
            "intact": intact,
        })
    return results
