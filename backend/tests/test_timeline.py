"""Tests for the Timeline CRUD and PATCH (link/unlink) API."""

import io
import pytest


def _make_evidence(client):
    resp = client.post(
        "/api/evidence",
        files={"file": ("tl.txt", io.BytesIO(b"timeline test"), "text/plain")},
        data={"title": "Timeline Test"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_create_timeline_event(client):
    resp = client.post(
        "/api/timeline",
        json={"title": "Launch Day", "occurred_at": "2024-01-15T00:00:00"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Launch Day"
    assert body["evidence_id"] is None


def test_create_with_evidence(client):
    ev_id = _make_evidence(client)
    resp = client.post(
        "/api/timeline",
        json={"title": "Linked Event", "occurred_at": "2024-06-01T00:00:00", "evidence_id": ev_id},
    )
    assert resp.status_code == 201
    assert resp.json()["evidence_id"] == ev_id


def test_list_timeline_ordered(client):
    client.post("/api/timeline", json={"title": "Later", "occurred_at": "2025-12-01T00:00:00"})
    client.post("/api/timeline", json={"title": "Earlier", "occurred_at": "2020-01-01T00:00:00"})
    resp = client.get("/api/timeline")
    assert resp.status_code == 200
    events = resp.json()
    dates = [e["occurred_at"] for e in events]
    assert dates == sorted(dates)


def test_patch_link_evidence(client):
    ev_id = _make_evidence(client)
    create = client.post(
        "/api/timeline",
        json={"title": "Patch Link Test", "occurred_at": "2024-03-01T00:00:00"},
    )
    tid = create.json()["id"]
    assert create.json()["evidence_id"] is None

    patch = client.patch(f"/api/timeline/{tid}", json={"evidence_id": ev_id})
    assert patch.status_code == 200
    assert patch.json()["evidence_id"] == ev_id
    assert patch.json()["title"] == "Patch Link Test"


def test_patch_unlink_evidence(client):
    ev_id = _make_evidence(client)
    create = client.post(
        "/api/timeline",
        json={"title": "Unlink Test", "occurred_at": "2024-04-01T00:00:00", "evidence_id": ev_id},
    )
    tid = create.json()["id"]

    patch = client.patch(f"/api/timeline/{tid}", json={"evidence_id": None})
    assert patch.status_code == 200
    assert patch.json()["evidence_id"] is None


def test_patch_updates_title(client):
    create = client.post(
        "/api/timeline",
        json={"title": "Old Title", "occurred_at": "2024-05-01T00:00:00"},
    )
    tid = create.json()["id"]
    patch = client.patch(f"/api/timeline/{tid}", json={"title": "New Title"})
    assert patch.status_code == 200
    assert patch.json()["title"] == "New Title"


def test_patch_not_found(client):
    resp = client.patch("/api/timeline/999999", json={"title": "Ghost"})
    assert resp.status_code == 404


def test_delete_event(client):
    create = client.post(
        "/api/timeline",
        json={"title": "Delete Me", "occurred_at": "2024-07-01T00:00:00"},
    )
    tid = create.json()["id"]
    del_resp = client.delete(f"/api/timeline/{tid}")
    assert del_resp.status_code == 204


def test_delete_not_found(client):
    resp = client.delete("/api/timeline/999999")
    assert resp.status_code == 404
