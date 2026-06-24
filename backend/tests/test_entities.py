"""Tests for the Entity CRUD and evidence-linking API."""

import io
import pytest


def _make_evidence(client, content=b"entity test doc"):
    resp = client.post(
        "/api/evidence",
        files={"file": ("ent.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Entity Test"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_create_entity(client):
    resp = client.post(
        "/api/entities",
        json={"name": "Jane Doe", "type": "PERSON", "description": "Test person"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Jane Doe"
    assert body["type"] == "PERSON"
    assert "id" in body


def test_list_entities(client):
    client.post("/api/entities", json={"name": "List Test Entity", "type": "COMPANY"})
    resp = client.get("/api/entities")
    assert resp.status_code == 200
    names = [e["name"] for e in resp.json()]
    assert "List Test Entity" in names


def test_search_entities(client):
    client.post("/api/entities", json={"name": "UniqueEntityABC999", "type": "BANK"})
    resp = client.get("/api/entities?q=UniqueEntityABC999")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert resp.json()[0]["name"] == "UniqueEntityABC999"


def test_get_entity(client):
    create = client.post("/api/entities", json={"name": "GetMe", "type": "OTHER"})
    eid = create.json()["id"]
    resp = client.get(f"/api/entities/{eid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == eid


def test_get_entity_not_found(client):
    resp = client.get("/api/entities/999999")
    assert resp.status_code == 404


def test_delete_entity(client):
    create = client.post("/api/entities", json={"name": "DeleteMe", "type": "OTHER"})
    eid = create.json()["id"]
    del_resp = client.delete(f"/api/entities/{eid}")
    assert del_resp.status_code == 204
    assert client.get(f"/api/entities/{eid}").status_code == 404


def test_link_and_unlink_evidence(client):
    ev_id = _make_evidence(client, b"link test content")
    create = client.post("/api/entities", json={"name": "Link Test Entity", "type": "PERSON"})
    eid = create.json()["id"]

    link = client.post(f"/api/entities/{eid}/link/{ev_id}?role=subject")
    assert link.status_code == 201
    assert link.json()["role"] == "subject"

    ev_entities = client.get(f"/api/evidence/{ev_id}/entities").json()
    assert any(e["id"] == eid for e in ev_entities)

    ent_evidence = client.get(f"/api/entities/{eid}/evidence").json()
    assert any(e["id"] == ev_id for e in ent_evidence)

    custody = client.get(f"/api/evidence/{ev_id}").json()["custody_events"]
    assert any(e["action"] == "LINKED" for e in custody)

    unlink = client.delete(f"/api/entities/{eid}/link/{ev_id}")
    assert unlink.status_code == 204

    ev_entities_after = client.get(f"/api/evidence/{ev_id}/entities").json()
    assert not any(e["id"] == eid for e in ev_entities_after)
