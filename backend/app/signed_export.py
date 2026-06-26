"""Signed export bundle for Veritas evidentiary vault.

Produces a tar.gz archive containing:
  manifest.json        — all evidence metadata + custody logs
  custody_log.json     — flat list of every ChainOfCustodyEvent
  timestamps/          — all .ots and .tsr timestamp receipts
  store/               — raw evidence objects (content-addressed)
  SIGNATURE            — Ed25519 signature over SHA-256(bundle bytes)
  PUBKEY               — public key in hex, for offline verification

The signing key is generated on first use and stored at
VERITAS_SIGNING_KEY_PATH (default: data/signing.key). The corresponding
public key is written alongside it as data/signing.pub.

Bundle verification (without Veritas):
  1. Remove SIGNATURE from the archive.
  2. Recompute SHA-256 of the remaining .tar.gz bytes.
  3. Verify the detached signature using the PUBKEY with any Ed25519 tool.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from .config import DATA_DIR, settings

logger = logging.getLogger(__name__)

_KEY_PATH = DATA_DIR / "signing.key"
_PUB_PATH = DATA_DIR / "signing.pub"


def _load_or_generate_key() -> Ed25519PrivateKey:
    if _KEY_PATH.exists():
        raw = _KEY_PATH.read_bytes()
        return Ed25519PrivateKey.from_private_bytes(raw)
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _KEY_PATH.write_bytes(raw)
    os.chmod(_KEY_PATH, 0o600)
    pub = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    _PUB_PATH.write_bytes(pub)
    logger.info("Generated new Ed25519 signing key: %s", _KEY_PATH)
    return key


def get_public_key_hex() -> str:
    key = _load_or_generate_key()
    pub = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return pub.hex()


def build_signed_bundle(
    manifest: dict,
    custody_log: list[dict],
    vault_id: str,
) -> tuple[bytes, str]:
    """Build a signed tar.gz bundle.

    Returns:
        (bundle_bytes, public_key_hex)
    """
    key = _load_or_generate_key()
    pub_hex = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    buf = io.BytesIO()

    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        def _add_bytes(name: str, data: bytes) -> None:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = int(datetime.now(timezone.utc).timestamp())
            tar.addfile(info, io.BytesIO(data))

        _add_bytes(
            "manifest.json",
            json.dumps(manifest, indent=2, default=str).encode("utf-8"),
        )
        _add_bytes(
            "custody_log.json",
            json.dumps(custody_log, indent=2, default=str).encode("utf-8"),
        )
        _add_bytes("PUBKEY", pub_hex.encode("ascii"))

        for d, arcname in [
            (settings.storage_dir, "store"),
            (settings.timestamp_dir, "timestamps"),
        ]:
            if d.exists():
                for fpath in sorted(d.rglob("*")):
                    if fpath.is_file():
                        rel = fpath.relative_to(d.parent)
                        try:
                            tar.add(fpath, arcname=str(Path(arcname) / fpath.relative_to(d)))
                        except Exception as exc:
                            logger.warning("Could not add %s to bundle: %s", fpath, exc)

    bundle_bytes = buf.getvalue()

    digest = hashlib.sha256(bundle_bytes).digest()
    sig = key.sign(digest)

    sig_buf = io.BytesIO()
    with tarfile.open(fileobj=sig_buf, mode="w:gz") as tar:
        def _add_bytes2(name: str, data: bytes) -> None:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = int(datetime.now(timezone.utc).timestamp())
            tar.addfile(info, io.BytesIO(data))

        manifest_json = json.dumps(manifest, indent=2, default=str).encode("utf-8")
        custody_json = json.dumps(custody_log, indent=2, default=str).encode("utf-8")
        sig_entry = json.dumps({
            "algorithm": "Ed25519",
            "sha256_of_unsigned_bundle": digest.hex(),
            "signature_hex": sig.hex(),
            "public_key_hex": pub_hex,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "vault_id": vault_id,
        }, indent=2).encode("utf-8")

        _add_bytes2("manifest.json", manifest_json)
        _add_bytes2("custody_log.json", custody_json)
        _add_bytes2("PUBKEY", pub_hex.encode("ascii"))
        _add_bytes2("SIGNATURE", sig_entry)

        for d, arcname in [
            (settings.storage_dir, "store"),
            (settings.timestamp_dir, "timestamps"),
        ]:
            if d.exists():
                for fpath in sorted(d.rglob("*")):
                    if fpath.is_file():
                        try:
                            tar.add(fpath, arcname=str(Path(arcname) / fpath.relative_to(d)))
                        except Exception as exc:
                            logger.warning("Could not add %s to bundle: %s", fpath, exc)

    return sig_buf.getvalue(), pub_hex


def verify_bundle(bundle_bytes: bytes) -> dict:
    """Verify a signed bundle produced by build_signed_bundle.

    Returns a dict with keys: valid (bool), error (str|None),
    public_key_hex, signed_at, vault_id.
    """
    try:
        buf = io.BytesIO(bundle_bytes)
        members: dict[str, bytes] = {}
        with tarfile.open(fileobj=buf, mode="r:gz") as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name in ("SIGNATURE", "PUBKEY"):
                    f = tar.extractfile(member)
                    if f:
                        members[member.name] = f.read()

        if "SIGNATURE" not in members:
            return {"valid": False, "error": "SIGNATURE file not found in bundle"}
        if "PUBKEY" not in members:
            return {"valid": False, "error": "PUBKEY file not found in bundle"}

        sig_data = json.loads(members["SIGNATURE"])
        pub_hex = sig_data["public_key_hex"]
        sig_hex = sig_data["signature_hex"]
        claimed_digest = bytes.fromhex(sig_data["sha256_of_unsigned_bundle"])

        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
        pub_key.verify(bytes.fromhex(sig_hex), claimed_digest)

        return {
            "valid": True,
            "error": None,
            "public_key_hex": pub_hex,
            "signed_at": sig_data.get("signed_at"),
            "vault_id": sig_data.get("vault_id"),
            "sha256_of_bundle": claimed_digest.hex(),
        }
    except Exception as exc:
        return {"valid": False, "error": str(exc), "public_key_hex": None}
