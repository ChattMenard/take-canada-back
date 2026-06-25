"""Tests for RFC 3161 external timestamping endpoints."""

import io

import pytest

from app.config import settings


@pytest.fixture
def evidence_id(client):
    resp = client.post(
        "/api/evidence",
        files={"file": ("ts.txt", io.BytesIO(b"rfc3161 test"), "text/plain")},
        data={"title": "RFC 3161 Test"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def rfc3161_enabled(monkeypatch):
    monkeypatch.setattr(settings, "rfc3161_enabled", True)
    yield


@pytest.fixture
def rfc3161_disabled(monkeypatch):
    monkeypatch.setattr(settings, "rfc3161_enabled", False)
    yield


def test_rfc3161_status_not_created(client, evidence_id):
    resp = client.get(f"/api/evidence/{evidence_id}/timestamp/rfc3161")
    assert resp.status_code == 200
    body = resp.json()
    assert body["timestamped"] is False
    assert body["verified"] is False


def test_rfc3161_create_disabled(client, evidence_id, rfc3161_disabled):
    resp = client.post(f"/api/evidence/{evidence_id}/timestamp/rfc3161")
    assert resp.status_code == 503


def test_rfc3161_create_and_verify_mocked(
    client, evidence_id, monkeypatch, tmp_path, rfc3161_enabled
):
    tsr_bytes = b"fake-tsr-data"
    stored = {}

    async def fake_store_tsr(sha256):
        stored[sha256] = tsr_bytes
        return tsr_bytes

    def fake_tsr_exists(sha256):
        return sha256 in stored

    def fake_tsr_path(sha256):
        p = tmp_path / f"{sha256}.tsr"
        if sha256 in stored:
            p.write_bytes(stored[sha256])
        return p

    monkeypatch.setattr("app.routers.evidence.rfc3161.store_tsr", fake_store_tsr)
    monkeypatch.setattr("app.routers.evidence.rfc3161.tsr_exists", fake_tsr_exists)
    monkeypatch.setattr("app.routers.evidence.rfc3161.tsr_path", fake_tsr_path)

    async def fake_verify(sha256):
        return {
            "exists": True,
            "verified": False,
            "error": None,
        }

    monkeypatch.setattr("app.routers.evidence.rfc3161.verify", fake_verify)

    create = client.post(f"/api/evidence/{evidence_id}/timestamp/rfc3161")
    assert create.status_code == 201
    body = create.json()
    assert body["timestamped"] is True

    status = client.get(f"/api/evidence/{evidence_id}/timestamp/rfc3161")
    assert status.json()["timestamped"] is True

    file_resp = client.get(f"/api/evidence/{evidence_id}/timestamp/rfc3161/file")
    assert file_resp.status_code == 200
    assert file_resp.content == tsr_bytes

    async def fake_verify_success(sha256):
        return {
            "exists": True,
            "verified": True,
            "error": None,
        }

    monkeypatch.setattr("app.routers.evidence.rfc3161.verify", fake_verify_success)
    verify = client.get(f"/api/evidence/{evidence_id}/timestamp/rfc3161")
    assert verify.status_code == 200
    assert verify.json()["verified"] is True

    detail = client.get(f"/api/evidence/{evidence_id}").json()
    custody_actions = [e["action"] for e in detail["custody_events"]]
    assert "ANNOTATED" in custody_actions


def test_rfc3161_file_not_found(client, evidence_id):
    resp = client.get(f"/api/evidence/{evidence_id}/timestamp/rfc3161/file")
    assert resp.status_code == 404
