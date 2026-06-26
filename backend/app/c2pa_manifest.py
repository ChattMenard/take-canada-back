"""C2PA content provenance manifest generation.

This module creates C2PA (Coalition for Content Provenance and Authenticity) 
manifests for evidence files, enabling interoperable digital provenance verification
across the global C2PA ecosystem.

C2PA v2.2 adds video streaming support, extended file format coverage, and updated
Trust List infrastructure. The U.S. Digital Authenticity and Provenance Act (2025)
mandates content provenance disclosure for federally regulated media contexts.
"""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from .config import settings

logger = logging.getLogger(__name__)

# C2PA is optional - if not installed, manifest generation is disabled
try:
    from c2pa import Builder, Signer
    C2PA_AVAILABLE = True
except ImportError:
    C2PA_AVAILABLE = False
    logger.warning("c2pa library not installed - C2PA manifest generation disabled")


def c2pa_manifest_path(sha256: str) -> Path:
    """Return the path for a C2PA manifest file for a given evidence hash."""
    return settings.storage_dir / f"{sha256}.c2pa.json"


def c2pa_manifest_exists(sha256: str) -> bool:
    """Check if a C2PA manifest exists for the given hash."""
    return c2pa_manifest_path(sha256).exists()


class C2PAError(Exception):
    """Raised when C2PA manifest generation fails."""
    pass


def create_manifest(
    file_bytes: bytes,
    filename: str,
    source_url: str | None = None,
    collected_by: str | None = None,
    title: str | None = None,
) -> dict:
    """Create a C2PA manifest for the given file.
    
    Args:
        file_bytes: The raw file content
        filename: Original filename
        source_url: Source URL if collected from web
        collected_by: Person/handle who collected the evidence
        title: Evidence title/description
        
    Returns:
        Dictionary containing manifest data
        
    Raises:
        C2PAError: If C2PA is not available or manifest generation fails
    """
    if not C2PA_AVAILABLE:
        raise C2PAError("C2PA library not installed")
    
    if not settings.c2pa_enabled:
        raise C2PAError("C2PA manifest generation is disabled in settings")
    
    try:
        # Calculate file hash for manifest
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        
        # Build C2PA manifest
        builder = Builder(
            "application/json",
            title=title or filename,
        )
        
        # Add provenance assertion
        builder.add_assertion(
            "https://ns.adobe.com/xap/1.0/mm/",
            {
                "xmpMM:DocumentID": sha256,
                "xmpMM:InstanceID": f"urn:uuid:{sha256}",
                "xmpMM:DerivedFrom": {
                    "stRef:instanceID": source_url or "unknown",
                    "stRef:documentID": source_url or "unknown",
                } if source_url else None,
            }
        )
        
        # Add Veritas-specific provenance
        builder.add_assertion(
            "https://veritas.provenance/ns/1.0",
            {
                "collector": collected_by or "unknown",
                "collectionTimestamp": datetime.now(timezone.utc).isoformat(),
                "sourceUrl": source_url,
                "filename": filename,
                "fileSize": len(file_bytes),
                "fileHash": {
                    "algorithm": "sha-256",
                    "value": sha256,
                },
            }
        )
        
        # Sign if certificates are provided
        if settings.c2pa_cert_path and settings.c2pa_key_path:
            try:
                signer = Signer(
                    settings.c2pa_cert_path,
                    settings.c2pa_key_path,
                    sign_alg="es256"  # ECDSA with SHA-256
                )
                builder.sign(signer)
            except Exception as exc:
                logger.warning("C2PA signing failed, generating unsigned manifest: %s", exc)
        
        # Generate manifest
        manifest = builder.build()
        
        return manifest
        
    except Exception as exc:
        logger.error("C2PA manifest generation failed: %s", exc)
        raise C2PAError(f"Failed to generate C2PA manifest: {exc}") from exc


def store_manifest(sha256: str, manifest: dict) -> Path:
    """Store a C2PA manifest to disk."""
    import json
    
    path = c2pa_manifest_path(sha256)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return path


def get_manifest(sha256: str) -> dict | None:
    """Load and return a C2PA manifest if it exists."""
    import json
    
    path = c2pa_manifest_path(sha256)
    if not path.exists():
        return None
    
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Failed to load C2PA manifest for %s: %s", sha256, exc)
        return None


async def create_and_store_manifest(
    file_bytes: bytes,
    filename: str,
    source_url: str | None = None,
    collected_by: str | None = None,
    title: str | None = None,
) -> dict:
    """Create and store a C2PA manifest for evidence.
    
    This is the main entry point for C2PA manifest generation during evidence ingest.
    """
    try:
        manifest = create_manifest(file_bytes, filename, source_url, collected_by, title)
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        store_manifest(sha256, manifest)
        return manifest
    except C2PAError:
        # Log but don't fail the entire ingest if C2PA fails
        logger.warning("C2PA manifest generation failed, continuing without manifest")
        return None
