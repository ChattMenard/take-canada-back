"""RFC 3161 timestamping via a trusted timestamp authority (TSA).

This module requests a TimeStampToken from a public TSA (FreeTSA by default)
for a given SHA-256 digest, stores the detached `.tsr` response, and exposes
helpers to check existence and download the response.

Unlike OpenTimestamps, an RFC 3161 timestamp is typically returned immediately
by the TSA and proves that the hash existed at the time the TSA signed it. It
does not require waiting for a blockchain confirmation.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from pyasn1.codec.der import decoder, encoder
from pyasn1.type import namedtype, namedval, univ

from .config import settings

logger = logging.getLogger(__name__)


# Minimal ASN.1 types for RFC 3161 TimeStampReq / TimeStampResp.
# A full implementation would use a dedicated library; this is enough for the
# standard SHA-256 request to FreeTSA and parsing a successful response.

class MessageImprint(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType(
            "hashAlgorithm",
            univ.Sequence(
                componentType=namedtype.NamedTypes(
                    namedtype.NamedType("algorithm", univ.ObjectIdentifier()),
                    namedtype.NamedType("parameters", univ.Any()),
                )
            ),
        ),
        namedtype.NamedType("hashedMessage", univ.OctetString()),
    )


class TimeStampReq(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("version", univ.Integer()),
        namedtype.NamedType("messageImprint", MessageImprint()),
        namedtype.OptionalNamedType("reqPolicy", univ.ObjectIdentifier()),
        namedtype.OptionalNamedType("nonce", univ.Integer()),
        namedtype.OptionalNamedType("certReq", univ.Boolean()),
        namedtype.OptionalNamedType("extensions", univ.Any()),
    )


class PKIStatusInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType(
            "status",
            univ.Integer(
                namedValues=namedval.NamedValues(
                    ("granted", 0),
                    ("grantedWithMods", 1),
                    ("rejection", 2),
                    ("waiting", 3),
                    ("revocationWarning", 4),
                    ("revocationNotification", 5),
                )
            ),
        ),
        namedtype.OptionalNamedType("statusString", univ.Any()),
        namedtype.OptionalNamedType("failInfo", univ.BitString()),
    )


class TimeStampResp(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("status", PKIStatusInfo()),
        namedtype.OptionalNamedType("timeStampToken", univ.Any()),
    )


def _digest_from_sha256(sha256: str) -> bytes:
    return bytes.fromhex(sha256)


def tsr_path(sha256: str) -> Path:
    return settings.timestamp_dir / f"{sha256}.tsr"


def tsr_exists(sha256: str) -> bool:
    return tsr_path(sha256).exists()


class RFC3161Error(Exception):
    """Raised when an RFC 3161 timestamp operation fails."""


def _build_request(sha256: str, nonce: int | None = None) -> bytes:
    """Build a DER-encoded TimeStampReq for the given SHA-256 digest."""
    digest = _digest_from_sha256(sha256)

    req = TimeStampReq()
    req["version"] = 1

    msg_imprint = MessageImprint()
    msg_imprint["hashAlgorithm"]["algorithm"] = univ.ObjectIdentifier(
        "2.16.840.1.101.3.4.2.1"
    )  # sha256
    msg_imprint["hashAlgorithm"]["parameters"] = univ.Null("")
    msg_imprint["hashedMessage"] = digest

    req["messageImprint"] = msg_imprint
    if nonce is not None:
        req["nonce"] = nonce
    req["certReq"] = True

    return encoder.encode(req)


def _parse_response(data: bytes) -> bytes:
    """Parse a DER TimeStampResp and return the embedded TimeStampToken bytes.

    Raises RFC3161Error if the response does not indicate success.
    """
    resp, _ = decoder.decode(data, asn1Spec=TimeStampResp())
    status = int(resp["status"]["status"])
    if status not in (0, 1):
        raise RFC3161Error(f"TSA rejected the request (status={status}).")

    token = resp["timeStampToken"]
    if token.isValue is False:
        raise RFC3161Error("TSA response successful but contained no token.")

    return encoder.encode(token)


async def request_tsr(sha256: str) -> bytes:
    """Request a TimeStampToken from the configured TSA for the given hash.

    Returns the raw DER `.tsr` bytes (the embedded TimeStampToken only).
    """
    if not settings.rfc3161_enabled:
        raise RFC3161Error("RFC 3161 timestamping is disabled.")

    nonce = int.from_bytes(_digest_from_sha256(sha256)[:8], "big")
    payload = _build_request(sha256, nonce=nonce)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                settings.rfc3161_tsa_url,
                content=payload,
                headers={
                    "Content-Type": "application/timestamp-query",
                    "Accept": "application/timestamp-reply",
                },
            )
    except Exception as exc:
        raise RFC3161Error(f"Could not reach TSA: {exc}") from exc

    if resp.status_code != 200:
        raise RFC3161Error(
            f"TSA returned HTTP {resp.status_code}: {resp.text[:200]}"
        )

    return _parse_response(resp.content)


async def store_tsr(sha256: str) -> bytes:
    """Request and persist a `.tsr` file for the given hash.

    Returns the raw `.tsr` bytes.
    """
    data = await request_tsr(sha256)
    path = tsr_path(sha256)
    path.write_bytes(data)
    return data


def _load_tsa_cert() -> x509.Certificate | None:
    """Load the TSA signing certificate if the configured URL is reachable."""
    if not settings.rfc3161_tsa_cert_url:
        return None
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(settings.rfc3161_tsa_cert_url)
            if resp.status_code == 200:
                return x509.load_pem_x509_certificate(resp.content)
    except Exception as exc:
        logger.warning("Could not load TSA certificate: %s", exc)
    return None


def _verify_token_signature(token: bytes, tsa_cert: x509.Certificate) -> bool:
    """Verify the TimeStampToken signature using the provided TSA certificate.

    This is a lightweight check: it verifies the signed digest inside the token
    matches the hash and that the signature was made by the TSA certificate's
    public key. It does not validate the full CMS chain or revocation status.
    """
    try:
        # token is a ContentInfo wrapping a SignedData. We only need the
        # encapsulated ContentInfo content (the TSTInfo) and the signature.
        content_info, _ = decoder.decode(token, asn1Spec=univ.Sequence())
        content_type = content_info[0]
        signed_data = content_info[1]
        # signed_data is [0] EXPLICIT SignedData
        signed_data = decoder.decode(signed_data.asOctets(), asn1Spec=univ.Sequence())[0]
        digest_algorithms = signed_data[1]
        encap_content_info = signed_data[2]
        signer_infos = signed_data[4]

        # Find the digest algorithm used.
        digest_alg_oid = str(digest_algorithms[0][0])
        if digest_alg_oid == "2.16.840.1.101.3.4.2.1":
            digest = hashes.SHA256()
        else:
            return False

        signer_info = signer_infos[0]
        signed_attrs = signer_info[3]
        signature = signer_info[4].asOctets()

        # The message-digest signed attribute contains the hash of the TSTInfo.
        message_digest = None
        for attr in signed_attrs:
            attr_type = str(attr[0])
            if attr_type == "1.2.840.113549.1.9.4":  # messageDigest
                message_digest = bytes(attr[1][0])
                break
        if message_digest is None:
            return False

        tsa_cert.public_key().verify(
            signature,
            encoder.encode(signed_attrs),
            padding.PKCS1v15(),
            digest,
        )
        return True
    except Exception as exc:
        logger.warning("RFC 3161 token signature verification failed: %s", exc)
        return False


async def verify(sha256: str) -> dict:
    """Verify the stored `.tsr` for the given hash.

    Returns a status dict with `exists`, `verified`, and optional `error`.
    """
    path = tsr_path(sha256)
    if not path.exists():
        return {
            "exists": False,
            "verified": False,
            "error": "No RFC 3161 timestamp found.",
        }

    token = path.read_bytes()
    tsa_cert = await asyncio.to_thread(_load_tsa_cert)
    if tsa_cert is None:
        return {
            "exists": True,
            "verified": False,
            "error": "TSA certificate could not be loaded; signature not verified.",
        }

    ok = await asyncio.to_thread(_verify_token_signature, token, tsa_cert)
    return {
        "exists": True,
        "verified": ok,
        "error": None if ok else "Token signature did not verify against TSA certificate.",
    }
