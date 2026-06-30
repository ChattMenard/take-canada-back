"""Text extraction for full-text search indexing.

Supports: PDF (pdfminer.six), HTML (beautifulsoup4), and plain text.
Falls back to an empty string on any error so ingest is never blocked.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_CHARS = 500_000  # cap to avoid giant FTS rows


def extract_text(data: bytes, content_type: str) -> str:
    """Return extracted plain text from raw bytes, or empty string on failure."""
    mime = content_type.split(";")[0].strip().lower()
    try:
        if mime == "application/pdf":
            return _from_pdf(data)
        if mime in ("text/html", "application/xhtml+xml"):
            return _from_html(data)
        if mime.startswith("text/"):
            return _from_plain(data)
    except Exception as exc:
        logger.warning("Text extraction failed (%s): %s", mime, exc)
    return ""


def _from_pdf(data: bytes) -> str:
    from io import BytesIO

    from pdfminer.high_level import extract_text as pdf_extract

    text = pdf_extract(BytesIO(data))
    return (text or "")[:_MAX_CHARS]


def _from_html(data: bytes) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(data, "html.parser")
    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text[:_MAX_CHARS]


def _from_plain(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="replace")[:_MAX_CHARS]
    except Exception:
        return ""
