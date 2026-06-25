"""Tests for the Evidence Vault API endpoints."""

import io
import pytest


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ingest_file(client):
    data = b"This is a test document."
    resp = client.post(
        "/api/evidence",
        files={"file": ("test.txt", io.BytesIO(data), "text/plain")},
        data={"title": "Test Doc", "collected_by": "tester"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Test Doc"
    assert len(body["sha256"]) == 64
    assert body["size_bytes"] == len(data)
    assert body["custody_events"][0]["action"] == "CREATED"


def test_ingest_empty_file_rejected(client):
    resp = client.post(
        "/api/evidence",
        files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
    )
    assert resp.status_code == 422


def test_ingest_deduplicates(client):
    data = b"duplicate content for dedup test"
    kwargs = dict(
        files={"file": ("dup.txt", io.BytesIO(data), "text/plain")},
        data={"title": "Dup 1"},
    )
    r1 = client.post("/api/evidence", files={"file": ("dup.txt", io.BytesIO(data), "text/plain")}, data={"title": "Dup 1"})
    r2 = client.post("/api/evidence", files={"file": ("dup.txt", io.BytesIO(data), "text/plain")}, data={"title": "Dup 2"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["sha256"] == r2.json()["sha256"]


def test_list_evidence(client):
    resp = client.get("/api/evidence")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_evidence(client):
    data = b"get test content"
    create = client.post(
        "/api/evidence",
        files={"file": ("get_test.txt", io.BytesIO(data), "text/plain")},
        data={"title": "Get Test"},
    )
    ev_id = create.json()["id"]
    resp = client.get(f"/api/evidence/{ev_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == ev_id


def test_get_evidence_not_found(client):
    resp = client.get("/api/evidence/999999")
    assert resp.status_code == 404


def test_verify_evidence(client):
    data = b"verify me"
    create = client.post(
        "/api/evidence",
        files={"file": ("verify.txt", io.BytesIO(data), "text/plain")},
    )
    ev_id = create.json()["id"]
    resp = client.post(f"/api/evidence/{ev_id}/verify")
    assert resp.status_code == 200
    body = resp.json()
    assert body["intact"] is True
    assert body["evidence_id"] == ev_id


def test_verify_creates_custody_event(client):
    data = b"custody chain test"
    create = client.post(
        "/api/evidence",
        files={"file": ("chain.txt", io.BytesIO(data), "text/plain")},
    )
    ev_id = create.json()["id"]
    client.post(f"/api/evidence/{ev_id}/verify")
    detail = client.get(f"/api/evidence/{ev_id}").json()
    actions = [e["action"] for e in detail["custody_events"]]
    assert "CREATED" in actions
    assert "VERIFIED" in actions


def test_add_note(client):
    data = b"note test"
    create = client.post(
        "/api/evidence",
        files={"file": ("note.txt", io.BytesIO(data), "text/plain")},
    )
    ev_id = create.json()["id"]
    resp = client.post(
        f"/api/evidence/{ev_id}/note",
        json={"actor": "analyst", "detail": "Looks relevant."},
    )
    assert resp.status_code == 200
    events = resp.json()["custody_events"]
    assert any(e["action"] == "ANNOTATED" and e["actor"] == "analyst" for e in events)


def test_patch_metadata(client):
    data = b"patch test"
    create = client.post(
        "/api/evidence",
        files={"file": ("patch.txt", io.BytesIO(data), "text/plain")},
        data={"title": "Original"},
    )
    ev_id = create.json()["id"]
    resp = client.patch(f"/api/evidence/{ev_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_search_metadata(client):
    data = b"searchable document"
    client.post(
        "/api/evidence",
        files={"file": ("search.txt", io.BytesIO(data), "text/plain")},
        data={"title": "UniqueSearchableTitleXYZ123"},
    )
    resp = client.get("/api/evidence?q=UniqueSearchableTitleXYZ123")
    assert resp.status_code == 200
    results = resp.json()
    assert any("UniqueSearchableTitleXYZ123" in r["title"] for r in results)


def test_download_evidence(client):
    data = b"downloadable content"
    create = client.post(
        "/api/evidence",
        files={"file": ("dl.txt", io.BytesIO(data), "text/plain")},
    )
    ev_id = create.json()["id"]
    resp = client.get(f"/api/evidence/{ev_id}/download")
    assert resp.status_code == 200
    assert resp.content == data


def test_stats(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "evidence_count" in body
    assert "storage_bytes" in body
