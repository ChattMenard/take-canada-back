"""Tests for vault export endpoints."""

import gzip
import io
from pathlib import Path


def _records(path: str) -> list[tuple[dict[str, str], bytes]]:
    data = gzip.decompress(Path(path).read_bytes())
    records = []
    pos = 0
    while pos < len(data):
        header_end = data.index(b"\r\n\r\n", pos)
        lines = data[pos:header_end].decode("utf-8").split("\r\n")
        headers = dict(line.split(": ", 1) for line in lines[1:])
        body_start = header_end + 4
        body_end = body_start + int(headers["Content-Length"])
        records.append((headers, data[body_start:body_end]))
        pos = body_end + 4
    return records


def test_export_warc_contains_evidence_resource_and_metadata(client):
    body = b"archival WARC fixture"
    created = client.post(
        "/api/evidence",
        files={"file": ("archive.txt", io.BytesIO(body), "text/plain")},
        data={
            "title": "Archive Fixture",
            "source_url": "https://example.org/archive.txt",
            "collected_by": "tester",
        },
    )
    assert created.status_code == 201

    resp = client.post("/api/export/warc?vault_id=test-warc")
    assert resp.status_code == 200
    result = resp.json()
    assert result["warc_path"].endswith("veritas-data-test-warc.warc.gz")
    assert result["warc_bytes"] > 0

    records = _records(result["warc_path"])
    assert [record[0]["WARC-Type"] for record in records].count("warcinfo") == 1
    assert any(
        headers["WARC-Type"] == "resource"
        and headers["WARC-Target-URI"] == "https://example.org/archive.txt"
        and headers["Content-Type"] == "text/plain"
        and payload == body
        for headers, payload in records
    )
    assert any(
        headers["WARC-Type"] == "metadata"
        and headers["WARC-Target-URI"] == "https://example.org/archive.txt"
        and b'"title": "Archive Fixture"' in payload
        for headers, payload in records
    )


def test_package_can_include_warc(client):
    resp = client.post(
        "/api/export/package?vault_id=test-package&include_store=false&include_warc=true"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["package_path"] is None
    assert body["warc_path"].endswith("veritas-data-test-package.warc.gz")
