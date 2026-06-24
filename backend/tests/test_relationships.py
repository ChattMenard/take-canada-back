"""Tests for the Relationship CRUD and evidence-linking API."""

import io
import pytest


def _make_entity(client, name, type_="PERSON"):
    resp = client.post("/api/entities", json={"name": name, "type": type_})
    assert resp.status_code == 201
    return resp.json()["id"]


def _make_evidence(client, content=b"rel test"):
    resp = client.post(
        "/api/evidence",
        files={"file": ("rel.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Rel Test"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_create_relationship(client):
    src = _make_entity(client, "Src Corp", "COMPANY")
    tgt = _make_entity(client, "Tgt Corp", "COMPANY")
    resp = client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "OWNERSHIP"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["kind"] == "OWNERSHIP"
    assert body["source_entity_id"] == src
    assert body["target_entity_id"] == tgt


def test_create_relationship_invalid_kind(client):
    src = _make_entity(client, "BadKind Src", "COMPANY")
    tgt = _make_entity(client, "BadKind Tgt", "COMPANY")
    resp = client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "MADE_UP_KIND"},
    )
    assert resp.status_code == 422


def test_create_relationship_missing_entity(client):
    resp = client.post(
        "/api/relationships",
        json={"source_entity_id": 999999, "target_entity_id": 999998, "kind": "OTHER"},
    )
    assert resp.status_code == 422


def test_list_relationships(client):
    src = _make_entity(client, "List Rel Src", "AGENCY")
    tgt = _make_entity(client, "List Rel Tgt", "PERSON")
    client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "EMPLOYMENT"},
    )
    resp = client.get("/api/relationships")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_relationships_by_entity(client):
    src = _make_entity(client, "Filter Src", "PERSON")
    tgt = _make_entity(client, "Filter Tgt", "BANK")
    create = client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "DONATION"},
    )
    rid = create.json()["id"]
    resp = client.get(f"/api/relationships?entity_id={src}")
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert rid in ids


def test_delete_relationship(client):
    src = _make_entity(client, "Del Rel Src", "COMPANY")
    tgt = _make_entity(client, "Del Rel Tgt", "COMPANY")
    create = client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "CONTRACT"},
    )
    rid = create.json()["id"]
    del_resp = client.delete(f"/api/relationships/{rid}")
    assert del_resp.status_code == 204


def test_link_evidence_to_relationship(client):
    src = _make_entity(client, "LinkEv Src", "COMPANY")
    tgt = _make_entity(client, "LinkEv Tgt", "PERSON")
    ev_id = _make_evidence(client, b"relationship evidence link test")
    create = client.post(
        "/api/relationships",
        json={"source_entity_id": src, "target_entity_id": tgt, "kind": "LOBBYING"},
    )
    rid = create.json()["id"]

    link = client.post(f"/api/relationships/{rid}/link/{ev_id}")
    assert link.status_code == 201

    rels = client.get("/api/relationships").json()
    rel = next(r for r in rels if r["id"] == rid)
    assert any(le["id"] == ev_id for le in rel["linked_evidence"])

    unlink = client.delete(f"/api/relationships/{rid}/link/{ev_id}")
    assert unlink.status_code == 204
