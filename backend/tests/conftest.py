"""Shared pytest fixtures for the Veritas backend test suite."""

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def tmp_data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("veritas_test_data")


@pytest.fixture(scope="session")
def client(tmp_data_dir):
    db_path = tmp_data_dir / "test.db"
    store_path = tmp_data_dir / "store"
    store_path.mkdir(exist_ok=True)

    os.environ["VERITAS_DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["VERITAS_STORAGE_DIR"] = str(store_path)
    os.environ["VERITAS_ALLOW_PRIVATE_COLLECT"] = "true"
    os.environ["VERITAS_TIMESTAMP_DIR"] = str(tmp_data_dir / "timestamps")
    os.environ["VERITAS_TIMESTAMP_ENABLED"] = "false"

    from app.config import settings

    settings.database_url = f"sqlite:///{db_path}"
    settings.storage_dir = store_path
    settings.timestamp_dir = tmp_data_dir / "timestamps"
    settings.timestamp_enabled = False

    from app.main import app
    from app.database import init_db

    init_db()

    with TestClient(app) as c:
        yield c
