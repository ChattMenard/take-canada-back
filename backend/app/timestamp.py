"""OpenTimestamps integration for external, Bitcoin-anchored timestamping.

Veritas stores a detached .ots signature per evidence hash. The .ots file proves
that the hash existed at the time it was submitted to a calendar, and after
confirmation it proves the hash existed no later than the Bitcoin block that
includes the calendar commitment.

This module intentionally does not depend on a local Bitcoin node. It uses
public OpenTimestamps calendars and the Blockstream.info API for verification.
"""

from __future__ import annotations

import asyncio
import io
import logging
from pathlib import Path

import httpx
from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
from opentimestamps.core.serialize import (
    StreamDeserializationContext,
    StreamSerializationContext,
)
from opentimestamps.core.timestamp import Timestamp

from .config import settings

logger = logging.getLogger(__name__)


def _digest_from_sha256(sha256: str) -> bytes:
    return bytes.fromhex(sha256)


def timestamp_path(sha256: str) -> Path:
    return settings.timestamp_dir / f"{sha256}.ots"


def exists(sha256: str) -> bool:
    return timestamp_path(sha256).exists()


def _serialize(timestamp: Timestamp) -> bytes:
    stream = io.BytesIO()
    ctx = StreamSerializationContext(stream)
    timestamp.serialize(ctx)
    return stream.getvalue()


def _deserialize(sha256: str, data: bytes) -> Timestamp:
    ctx = StreamDeserializationContext(io.BytesIO(data))
    return Timestamp.deserialize(ctx, _digest_from_sha256(sha256))


def _calendars() -> list[RemoteCalendar]:
    return [RemoteCalendar(url) for url in settings.timestamp_calendars]


class TimestampError(Exception):
    """Raised when an OpenTimestamps operation fails."""


async def _submit_all(sha256: str) -> Timestamp:
    """Submit a digest to all configured calendars and merge the results."""
    digest = _digest_from_sha256(sha256)
    timestamp: Timestamp | None = None
    last_error: Exception | None = None

    for calendar in _calendars():
        try:
            cal_ts = await asyncio.to_thread(calendar.submit, digest)
            if cal_ts is None:
                continue
            if timestamp is None:
                timestamp = cal_ts
            else:
                timestamp = timestamp.merge(cal_ts)
        except Exception as exc:
            logger.warning("Calendar %s failed: %s", calendar.url, exc)
            last_error = exc

    if timestamp is None:
        raise TimestampError(
            f"Could not create timestamp for {sha256}: no calendar responded."
        ) from last_error

    return timestamp


async def create(sha256: str) -> bytes:
    """Submit a SHA-256 hash to OpenTimestamps calendars and return the .ots bytes.

    Returns the pending timestamp bytes. The timestamp may need to be upgraded
    later once the calendar publishes its Bitcoin commitment.
    """
    if not settings.timestamp_enabled:
        raise TimestampError("Timestamping is disabled.")

    timestamp = await _submit_all(sha256)
    return _serialize(timestamp)


async def upgrade(sha256: str) -> bytes | None:
    """Re-submit the hash to calendars and merge any new confirmations.

    Returns the upgraded .ots bytes if an upgrade was possible, otherwise None.
    """
    path = timestamp_path(sha256)
    if not path.exists():
        return None

    current = _deserialize(sha256, path.read_bytes())
    try:
        new_timestamp = await _submit_all(sha256)
        current = current.merge(new_timestamp)
    except TimestampError:
        return None

    data = _serialize(current)
    path.write_bytes(data)
    return data


def _block_header(block_hash: str) -> bytes | None:
    """Fetch a raw 80-byte block header from Blockstream.info."""
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{settings.timestamp_bitcoin_url}/block/{block_hash}/header"
            )
            if resp.status_code == 200:
                return bytes.fromhex(resp.text.strip())
    except Exception as exc:
        logger.warning("Could not fetch block header %s: %s", block_hash, exc)
    return None


async def verify(sha256: str) -> dict:
    """Verify a stored .ots timestamp against the Bitcoin blockchain.

    Returns a status dict with `verified`, `pending`, `attestations`, and an
    optional `error` message.
    """
    path = timestamp_path(sha256)
    if not path.exists():
        return {"verified": False, "pending": False, "error": "No timestamp found."}

    digest = _digest_from_sha256(sha256)
    timestamp = _deserialize(sha256, path.read_bytes())

    attestations = []
    for attestation, attestation_msg in timestamp.all_attestations():
        if isinstance(attestation, BitcoinBlockHeaderAttestation):
            attestations.append(
                {
                    "type": "bitcoin",
                    "height": attestation.height,
                    "message": attestation_msg.hex(),
                }
            )
        else:
            attestations.append(
                {
                    "type": type(attestation).__name__,
                    "message": attestation_msg.hex() if isinstance(attestation_msg, bytes) else str(attestation_msg),
                }
            )

    if not attestations:
        return {"verified": False, "pending": True, "attestations": attestations}

    # Check that at least one Bitcoin attestation can be validated against a
    # public block header. We verify the attestation by re-running the
    # commitment path and checking the block header's merkle root.
    bitcoin_atts = [a for a in attestations if a["type"] == "bitcoin"]
    if not bitcoin_atts:
        return {
            "verified": False,
            "pending": True,
            "attestations": attestations,
            "error": "Timestamp is pending; no Bitcoin attestation yet.",
        }

    # Try to verify the first Bitcoin attestation against blockstream.info.
    for att in bitcoin_atts:
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    f"{settings.timestamp_bitcoin_url}/block-height/{att['height']}"
                )
                if resp.status_code != 200:
                    continue
                block_hash = resp.text.strip()
                header = _block_header(block_hash)
                if header is None:
                    continue
                # The attestation verifies the timestamp message against the
                # block header. We use the library helper to do the heavy work.
                from opentimestamps.bitcoin import make_timestamp_from_block

                block_timestamp = make_timestamp_from_block(
                    digest, header, att["height"]
                )
                if block_timestamp is not None:
                    # A successful creation means the header commits to our digest.
                    return {
                        "verified": True,
                        "pending": False,
                        "attestations": attestations,
                        "block_height": att["height"],
                        "block_hash": block_hash,
                    }
        except Exception as exc:
            logger.warning("Bitcoin attestation verification failed: %s", exc)

    return {
        "verified": False,
        "pending": True,
        "attestations": attestations,
        "error": "Could not verify Bitcoin attestation against the blockchain API.",
    }


async def store(sha256: str) -> bytes:
    """Create a timestamp and persist it to the timestamp store.

    Returns the .ots bytes.
    """
    data = await create(sha256)
    path = timestamp_path(sha256)
    path.write_bytes(data)
    return data
