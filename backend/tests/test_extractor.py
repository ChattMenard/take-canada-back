"""Tests for the text extractor module."""

import pytest


def test_extract_plain_text():
    from app.extractor import extract_text

    data = b"Hello, this is plain text."
    result = extract_text(data, "text/plain")
    assert "Hello" in result
    assert "plain text" in result


def test_extract_html():
    from app.extractor import extract_text

    html = b"<html><body><h1>Title</h1><p>Body content here.</p><script>js()</script></body></html>"
    result = extract_text(html, "text/html")
    assert "Title" in result
    assert "Body content here" in result
    assert "js()" not in result


def test_extract_html_with_charset():
    from app.extractor import extract_text

    html = b"<html><body><p>Charset test</p></body></html>"
    result = extract_text(html, "text/html; charset=utf-8")
    assert "Charset test" in result


def test_extract_unknown_mime_returns_empty():
    from app.extractor import extract_text

    data = b"\x00\x01\x02binary"
    result = extract_text(data, "application/octet-stream")
    assert result == ""


def test_extract_never_raises():
    from app.extractor import extract_text

    result = extract_text(b"\xff\xfe corrupt", "application/pdf")
    assert isinstance(result, str)
