"""WARC 1.1 export for archival interoperability."""

import gzip
import json
import shutil
from base64 import b32encode
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import Evidence
from .storage import get_path

CRLF = b"\r\n"
CHUNK = 1024 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _warc_date(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _record_id() -> str:
    return f"<urn:uuid:{uuid4()}>"


def _digest(sha256: str) -> str:
    return f"sha256:{b32encode(bytes.fromhex(sha256)).decode('ascii').rstrip('=')}"


def _target_uri(evidence: Evidence) -> str:
    return evidence.source_url or f"urn:sha256:{evidence.sha256}"


def _header_block(headers: dict[str, str | int]) -> bytes:
    return (
        b"WARC/1.1\r\n"
        + b"".join(f"{key}: {value}\r\n".encode("utf-8") for key, value in headers.items())
        + CRLF
    )


def _json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode(
        "utf-8"
    )


def _warcinfo_bytes(fields: dict[str, str | int]) -> bytes:
    return b"".join(
        f"{key}: {value}\r\n".encode("utf-8") for key, value in fields.items()
    )


def _write_member(fh, header: bytes, body: bytes | Path) -> None:
    with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
        gz.write(header)
        if isinstance(body, Path):
            with body.open("rb") as src:
                shutil.copyfileobj(src, gz, length=CHUNK)
        else:
            gz.write(body)
        gz.write(CRLF + CRLF)


def write_warc(path: Path, evidence_items: list[Evidence], *, vault_id: str) -> Path:
    """Write a compressed WARC file containing all evidence objects.

    Each evidence item is exported as:
      * a WARC `resource` record with the exact stored object bytes
      * a WARC `metadata` record with Veritas provenance and integrity fields
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    warc_date = _now()

    with path.open("wb") as fh:
        info = _warcinfo_bytes(
            {
                "software": "Veritas Evidentiary Collection Engine",
                "format": "WARC File Format 1.1",
                "vault-id": vault_id,
                "generated-at": warc_date,
                "record-count": len(evidence_items),
            }
        )
        _write_member(
            fh,
            _header_block(
                {
                    "WARC-Type": "warcinfo",
                    "WARC-Date": warc_date,
                    "WARC-Record-ID": _record_id(),
                    "Content-Type": "application/warc-fields",
                    "Content-Length": len(info),
                }
            ),
            info,
        )

        for evidence in evidence_items:
            object_path = get_path(evidence.sha256)
            if not object_path.exists():
                raise FileNotFoundError(
                    f"Stored object missing for evidence {evidence.id}: {evidence.sha256}"
                )

            digest = _digest(evidence.sha256)
            resource_id = _record_id()
            _write_member(
                fh,
                _header_block(
                    {
                        "WARC-Type": "resource",
                        "WARC-Date": _warc_date(evidence.created_at),
                        "WARC-Record-ID": resource_id,
                        "WARC-Target-URI": _target_uri(evidence),
                        "WARC-Payload-Digest": digest,
                        "WARC-Block-Digest": digest,
                        "Content-Type": evidence.content_type or "application/octet-stream",
                        "Content-Length": object_path.stat().st_size,
                    }
                ),
                object_path,
            )

            metadata = _json_bytes(
                {
                    "id": evidence.id,
                    "sha256": evidence.sha256,
                    "title": evidence.title,
                    "filename": evidence.filename,
                    "content_type": evidence.content_type,
                    "size_bytes": evidence.size_bytes,
                    "source_url": evidence.source_url,
                    "source_description": evidence.source_description,
                    "captured_at": evidence.captured_at,
                    "collected_by": evidence.collected_by,
                    "notes": evidence.notes,
                    "created_at": evidence.created_at,
                }
            )
            _write_member(
                fh,
                _header_block(
                    {
                        "WARC-Type": "metadata",
                        "WARC-Date": warc_date,
                        "WARC-Record-ID": _record_id(),
                        "WARC-Target-URI": _target_uri(evidence),
                        "WARC-Refers-To": resource_id,
                        "Content-Type": "application/json",
                        "Content-Length": len(metadata),
                    }
                ),
                metadata,
            )

    return path
