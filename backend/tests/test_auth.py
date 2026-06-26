"""Tests for authentication helpers."""

from app.auth import get_password_hash, verify_password


def test_bcrypt_password_hash_roundtrip():
    password_hash = get_password_hash("correct horse battery staple")
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong", password_hash)


def test_malformed_password_hash_fails_closed():
    assert not verify_password("password", "not-a-bcrypt-hash")
