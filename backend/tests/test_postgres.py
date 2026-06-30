"""Smoke tests for PostgreSQL backend support.

Requires a running PostgreSQL server and a database named `TAKE_CANADA_BACK_test` owned
by a user `TAKE_CANADA_BACK` with password `TAKE_CANADA_BACK`. To skip, set TAKE_CANADA_BACK_SKIP_POSTGRES=1.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def pg_client():
    if os.environ.get("TAKE_CANADA_BACK_SKIP_POSTGRES") == "1":
        pytest.skip("PostgreSQL tests skipped by TAKE_CANADA_BACK_SKIP_POSTGRES")

    os.environ["TAKE_CANADA_BACK_DATABASE_URL"] = "postgresql://TAKE_CANADA_BACK:TAKE_CANADA_BACK@localhost:5432/TAKE_CANADA_BACK_test"
    os.environ["TAKE_CANADA_BACK_STORAGE_DIR"] = "/tmp/TAKE_CANADA_BACK_pg_store"
    os.environ["TAKE_CANADA_BACK_TIMESTAMP_DIR"] = "/tmp/TAKE_CANADA_BACK_pg_ts"
    os.environ["TAKE_CANADA_BACK_TIMESTAMP_ENABLED"] = "false"
    os.environ["TAKE_CANADA_BACK_ALLOW_PRIVATE_COLLECT"] = "true"

    store_path = Path("/tmp/TAKE_CANADA_BACK_pg_store")
    ts_path = Path("/tmp/TAKE_CANADA_BACK_pg_ts")
    store_path.mkdir(parents=True, exist_ok=True)
    ts_path.mkdir(parents=True, exist_ok=True)

    from app.config import settings

    settings.database_url = "postgresql://TAKE_CANADA_BACK:TAKE_CANADA_BACK@localhost:5432/TAKE_CANADA_BACK_test"
    settings.storage_dir = store_path
    settings.timestamp_dir = ts_path
    settings.timestamp_enabled = False

    from app.main import app
    from app.database import init_db

    init_db()

    with TestClient(app) as client:
        yield client


def test_postgres_ingest_and_search(pg_client):
    resp = pg_client.post(
        "/api/evidence",
        files={"file": ("pg.txt", __import__("io").BytesIO(b"postgresql test content"), "text/plain")},
        data={"title": "PG Test", "notes": "searchable note"},
    )
    assert resp.status_code == 201
    ev = resp.json()
    assert ev["title"] == "PG Test"

    search = pg_client.get("/api/evidence?q=searchable")
    assert search.status_code == 200
    results = search.json()
    assert any(r["id"] == ev["id"] for r in results)

    verify = pg_client.post(f"/api/evidence/{ev['id']}/verify")
    assert verify.status_code == 200
    assert verify.json()["intact"] is True

    stats = pg_client.get("/api/stats")
    assert stats.status_code == 200
    assert stats.json()["evidence_count"] >= 1
