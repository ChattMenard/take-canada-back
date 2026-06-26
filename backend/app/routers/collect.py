"""Batch and crawl collection endpoints for automated evidence ingestion."""

from __future__ import annotations

import asyncio
import re
from urllib.parse import urljoin, urlparse

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from .. import custody, storage
from ..config import settings
from ..database import get_session
from ..extractor import extract_text
from ..fetcher import FetchError, fetch_url
from ..models import ChainOfCustodyEvent, CustodyAction, Evidence
from ..routers.auth import get_current_admin
from ..routers.seal import ensure_unsealed

router = APIRouter(prefix="/api/collect", tags=["collect"])


class BatchUrlItem(BaseModel):
    url: str
    title: str | None = None
    source_description: str | None = None
    collected_by: str | None = None
    notes: str | None = None


class BatchRequest(BaseModel):
    items: list[BatchUrlItem]


class BatchResultItem(BaseModel):
    url: str
    success: bool
    evidence_id: int | None = None
    sha256: str | None = None
    error: str | None = None


class CrawlRequest(BaseModel):
    root_url: str
    link_pattern: str | None = None
    title_prefix: str | None = None
    collected_by: str | None = None
    notes: str | None = None


async def _ingest_one(item: BatchUrlItem, session: Session) -> BatchResultItem:
    try:
        res = await fetch_url(item.url)
    except FetchError as exc:
        return BatchResultItem(url=item.url, success=False, error=str(exc))

    sha256, _, size = storage.store_bytes(res.content)

    evidence = Evidence(
        sha256=sha256,
        title=item.title or res.filename or sha256[:12],
        filename=res.filename,
        content_type=res.content_type,
        size_bytes=size,
        source_url=res.final_url,
        source_description=item.source_description,
        collected_by=item.collected_by or settings.default_collector,
        notes=item.notes,
        extracted_text=extract_text(res.content, res.content_type) or None,
    )
    session.add(evidence)
    session.commit()
    session.refresh(evidence)

    custody.create_custody_event(
        session,
        evidence_id=evidence.id,
        action=CustodyAction.CREATED,
        actor=evidence.collected_by,
        detail=(
            f"Batch-collected from {item.url} "
            f"(HTTP {res.status_code}, {res.content_type}, {size} bytes). "
            f"Final URL: {res.final_url}."
        ),
        hash_at_event=sha256,
    )
    session.commit()

    return BatchResultItem(
        url=item.url, success=True, evidence_id=evidence.id, sha256=sha256
    )


@router.post("/batch", response_model=list[BatchResultItem])
async def batch_collect(
    request: BatchRequest,
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    """Collect multiple URLs concurrently. Returns per-URL success/fail."""
    ensure_unsealed()
    limit = min(len(request.items), settings.collect_batch_limit)
    tasks = [_ingest_one(item, session) for item in request.items[:limit]]
    return await asyncio.gather(*tasks)


@router.post("/crawl", response_model=list[BatchResultItem])
async def crawl_collect(
    request: CrawlRequest,
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    """Fetch root_url, discover first-level hrefs matching link_pattern, ingest each."""
    ensure_unsealed()
    try:
        root = await fetch_url(request.root_url)
    except FetchError as exc:
        return [BatchResultItem(url=request.root_url, success=False, error=str(exc))]

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(root.content, "html.parser")
    pattern = re.compile(request.link_pattern) if request.link_pattern else None

    seen: set[str] = set()
    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        absolute = urljoin(request.root_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        if pattern and not pattern.search(absolute):
            continue
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
        if len(links) >= settings.collect_batch_limit:
            break

    items = [
        BatchUrlItem(
            url=url,
            title=f"{request.title_prefix} {url}" if request.title_prefix else None,
            collected_by=request.collected_by or settings.default_collector,
            notes=request.notes,
        )
        for url in links
    ]

    tasks = [_ingest_one(item, session) for item in items]
    return await asyncio.gather(*tasks)
