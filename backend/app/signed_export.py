"""Signed export bundle functionality for Veritas.

Creates cryptographically signed export bundles that can be verified
offline without needing to trust the transport or storage medium.
"""

import json
from pathlib import Path
from typing import BinaryIO

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .config import settings


def get_signing_key_path() -> Path:
    """Get the path to the Ed25519 signing key."""
    return settings.data_dir / "signing.key"


def load_signing_key() -> Ed25519PrivateKey:
    """Load the Ed25519 signing key from disk."""
    key_path = get_signing_key_path()
    
    if not key_path.exists():
        # Generate a new key if none exists
        private_key = Ed25519PrivateKey.generate()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return private_key
    
    with open(key_path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def get_public_key() -> str:
    """Get the public key in PEM format."""
    private_key = load_signing_key()
    public_key = private_key.public_key()
    
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")


def sign_bundle(manifest: dict, bundle_data: bytes) -> dict:
    """Create a signed export bundle.
    
    Args:
        manifest: The vault manifest
        bundle_data: The raw bundle data (tar.gz or WARC)
        
    Returns:
        Dictionary containing the signed bundle
    """
    private_key = load_signing_key()
    
    # Create signature
    signature = private_key.sign(bundle_data)
    
    return {
        "manifest": manifest,
        "signature": signature.hex(),
        "public_key": get_public_key(),
        "algorithm": "Ed25519",
        "format": "veritas-signed-bundle-v1"
    }


def verify_bundle(signed_bundle: dict, bundle_data: bytes) -> bool:
    """Verify a signed export bundle.
    
    Args:
        signed_bundle: The signed bundle dictionary
        bundle_data: The raw bundle data
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Load public key
        public_key_bytes = signed_bundle["public_key"].encode("utf-8")
        public_key = serialization.load_pem_public_key(public_key_bytes)
        
        # Verify signature
        signature_bytes = bytes.fromhex(signed_bundle["signature"])
        public_key.verify(signature_bytes, bundle_data)
        
        return True
    except Exception:
        return False


def create_signed_bundle_from_files(manifest_path: Path, bundle_path: Path) -> dict:
    """Create a signed bundle from manifest and package files.
    
    Args:
        manifest_path: Path to the manifest JSON file
        bundle_path: Path to the bundle file (tar.gz or WARC)
        
    Returns:
        Dictionary containing the signed bundle
    """
    # Load manifest
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Load bundle data
    with open(bundle_path, "rb") as f:
        bundle_data = f.read()
    
    return sign_bundle(manifest, bundle_data)
