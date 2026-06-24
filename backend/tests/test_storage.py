"""Tests for the content-addressed object store."""

import hashlib

import pytest


def _setup_store(tmp_path, monkeypatch):
    from app import config as cfg

    store = tmp_path / "store"
    store.mkdir()
    monkeypatch.setattr(cfg.settings, "storage_dir", store)
    return store


def test_hash_bytes():
    from app.storage import hash_bytes

    data = b"hello veritas"
    expected = hashlib.sha256(data).hexdigest()
    assert hash_bytes(data) == expected


def test_store_bytes_creates_file(tmp_path, monkeypatch):
    from app.storage import store_bytes, get_path

    _setup_store(tmp_path, monkeypatch)
    data = b"test content for storage"
    sha256, path, size = store_bytes(data)

    assert path.exists()
    assert size == len(data)
    assert path.read_bytes() == data
    assert sha256 == hashlib.sha256(data).hexdigest()


def test_store_bytes_idempotent(tmp_path, monkeypatch):
    from app.storage import store_bytes

    store = _setup_store(tmp_path, monkeypatch)
    data = b"same bytes twice"
    sha1, path1, _ = store_bytes(data)
    sha2, path2, _ = store_bytes(data)

    assert sha1 == sha2
    assert path1 == path2
    assert len(list((store / sha1[:2]).iterdir())) == 1


def test_verify_intact(tmp_path, monkeypatch):
    from app.storage import store_bytes, verify

    _setup_store(tmp_path, monkeypatch)
    data = b"verifiable content"
    sha256, path, _ = store_bytes(data)
    assert verify(sha256) is True


def test_verify_tampered(tmp_path, monkeypatch):
    from app.storage import store_bytes, verify, get_path

    _setup_store(tmp_path, monkeypatch)
    data = b"original data"
    sha256, path, _ = store_bytes(data)
    path.write_bytes(b"tampered!")
    assert verify(sha256) is False


def test_verify_missing(tmp_path, monkeypatch):
    from app.storage import verify

    _setup_store(tmp_path, monkeypatch)
    assert verify("a" * 64) is False
