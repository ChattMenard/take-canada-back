"""Tests for OpenTimestamps external anchoring endpoints."""

import io

import pytest

from app.config import settings


@pytest.fixture
def evidence_id(client):
    resp = client.post(
        "/api/evidence",
        files={"file": ("ts.txt", io.BytesIO(b"timestamp test"), "text/plain")},
        data={"title": "Timestamp Test"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def timestamp_enabled(monkeypatch):
    monkeypatch.setattr(settings, "timestamp_enabled", True)
    yield


@pytest.fixture
def timestamp_disabled(monkeypatch):
    monkeypatch.setattr(settings, "timestamp_enabled", False)
    yield


def test_timestamp_status_not_created(client, evidence_id):
    resp = client.get(f"/api/evidence/{evidence_id}/timestamp")
    assert resp.status_code == 200
    body = resp.json()
    assert body["timestamped"] is False


def test_timestamp_create_disabled(client, evidence_id, timestamp_disabled):
    resp = client.post(f"/api/evidence/{evidence_id}/timestamp")
    assert resp.status_code == 503


def test_timestamp_create_and_verify_mocked(client, evidence_id, monkeypatch, tmp_path, timestamp_enabled):
    ots_bytes = b"fake-ots-data"
    stored = {}

    async def fake_store(sha256):
        stored[sha256] = ots_bytes
        return ots_bytes

    def fake_exists(sha256):
        return sha256 in stored

    def fake_path(sha256):
        p = tmp_path / f"{sha256}.ots"
        if sha256 in stored:
            p.write_bytes(stored[sha256])
        return p

    monkeypatch.setattr("app.routers.evidence.timestamp.store", fake_store)
    monkeypatch.setattr("app.routers.evidence.timestamp.exists", fake_exists)
    monkeypatch.setattr("app.routers.evidence.timestamp.timestamp_path", fake_path)

    create = client.post(f"/api/evidence/{evidence_id}/timestamp")
    assert create.status_code == 201
    assert create.json()["timestamped"] is True

    status = client.get(f"/api/evidence/{evidence_id}/timestamp")
    assert status.json()["timestamped"] is True

    file_resp = client.get(f"/api/evidence/{evidence_id}/timestamp/file")
    assert file_resp.status_code == 200
    assert file_resp.content == ots_bytes

    async def fake_verify(sha256):
        return {
            "verified": True,
            "pending": False,
            "attestations": [{"type": "bitcoin", "height": 800_000}],
            "block_height": 800_000,
            "block_hash": "0000000000000000000abc",
        }

    monkeypatch.setattr("app.routers.evidence.timestamp.verify", fake_verify)
    verify = client.post(f"/api/evidence/{evidence_id}/timestamp/verify")
    assert verify.status_code == 200
    assert verify.json()["verified"] is True
    assert verify.json()["block_height"] == 800_000

    # Upgrade should call the fake store and log an ANNOTATED event
    async def fake_upgrade(sha256):
        return b"upgraded"

    monkeypatch.setattr("app.routers.evidence.timestamp.upgrade", fake_upgrade)
    upgrade = client.post(f"/api/evidence/{evidence_id}/timestamp/upgrade")
    assert upgrade.status_code == 200

    detail = client.get(f"/api/evidence/{evidence_id}").json()
    custody_actions = [e["action"] for e in detail["custody_events"]]
    assert "ANNOTATED" in custody_actions
    assert "VERIFIED" in custody_actions
