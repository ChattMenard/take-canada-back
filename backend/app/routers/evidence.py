"""Evidence Vault API — ingest, preserve, verify, and audit source material."""

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import text as sa_text
from sqlmodel import Session, select

from .. import storage
from ..config import settings
from ..database import get_session
from ..extractor import extract_text
from ..fetcher import FetchError, fetch_url
from ..models import (
    ChainOfCustodyEvent,
    CustodyAction,
    Entity,
    Evidence,
    EvidenceEntityLink,
)
from ..schemas import (
    CustodyNote,
    EvidenceDetail,
    EvidenceMetadata,
    EvidenceRead,
    LinkedEntityRead,
    UrlCollect,
    VerifyResult,
)

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


def _log(session: Session, evidence_id: int, action: CustodyAction, *, actor: str | None,
         detail: str | None, hash_at_event: str | None) -> None:
    session.add(
        ChainOfCustodyEvent(
            evidence_id=evidence_id,
            action=action,
            actor=actor,
            detail=detail,
            hash_at_event=hash_at_event,
        )
    )


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(422, f"Invalid datetime: {value!r} (use ISO 8601)")


@router.post("", response_model=EvidenceDetail, status_code=201)
async def ingest_evidence(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    source_url: str | None = Form(None),
    source_description: str | None = Form(None),
    captured_at: str | None = Form(None),
    collected_by: str | None = Form(None),
    notes: str | None = Form(None),
    session: Session = Depends(get_session),
):
    data = await file.read()
    if not data:
        raise HTTPException(422, "Empty file.")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit.")

    sha256, _, size = storage.store_bytes(data)
    ct = file.content_type or "application/octet-stream"

    evidence = Evidence(
        sha256=sha256,
        title=title or file.filename or sha256[:12],
        filename=file.filename or "unnamed",
        content_type=ct,
        size_bytes=size,
        source_url=source_url,
        source_description=source_description,
        captured_at=_parse_dt(captured_at),
        collected_by=collected_by,
        notes=notes,
        extracted_text=extract_text(data, ct) or None,
    )
    session.add(evidence)
    session.commit()
    session.refresh(evidence)

    _log(
        session,
        evidence.id,
        CustodyAction.CREATED,
        actor=collected_by,
        detail=f"Ingested {evidence.filename} ({size} bytes)",
        hash_at_event=sha256,
    )
    session.commit()
    session.refresh(evidence)
    return evidence


@router.post("/collect-url", response_model=EvidenceDetail, status_code=201)
async def collect_from_url(payload: UrlCollect, session: Session = Depends(get_session)):
    """Fetch a public URL server-side, then hash, store, and file it as evidence."""
    try:
        res = await fetch_url(payload.url)
    except FetchError as exc:
        raise HTTPException(422, str(exc))

    sha256, _, size = storage.store_bytes(res.content)

    evidence = Evidence(
        sha256=sha256,
        title=payload.title or res.filename or sha256[:12],
        filename=res.filename,
        content_type=res.content_type,
        size_bytes=size,
        source_url=res.final_url,
        source_description=payload.source_description,
        captured_at=payload.captured_at,
        collected_by=payload.collected_by,
        notes=payload.notes,
        extracted_text=extract_text(res.content, res.content_type) or None,
    )
    session.add(evidence)
    session.commit()
    session.refresh(evidence)

    _log(
        session,
        evidence.id,
        CustodyAction.CREATED,
        actor=payload.collected_by,
        detail=(
            f"Collected from URL {payload.url} "
            f"(HTTP {res.status_code}, {res.content_type}, {size} bytes). "
            f"Final URL after redirects: {res.final_url}. "
            f"Retrieved {res.fetched_at.isoformat()}."
        ),
        hash_at_event=sha256,
    )
    session.commit()
    session.refresh(evidence)
    return evidence


@router.get("", response_model=list[EvidenceRead])
def list_evidence(
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    capped = min(limit, 500)
    if q:
        fts_ids = session.exec(
            sa_text(
                "SELECT rowid FROM evidence_fts WHERE evidence_fts MATCH :q ORDER BY rank LIMIT :lim"
            ).bindparams(q=q, lim=capped + offset)
        ).fetchall()
        if fts_ids:
            id_list = [row[0] for row in fts_ids][offset : offset + capped]
            stmt = (
                select(Evidence)
                .where(Evidence.id.in_(id_list))
                .order_by(Evidence.created_at.desc())
            )
            return session.exec(stmt).all()
        like = f"%{q}%"
        stmt = (
            select(Evidence)
            .where(
                Evidence.title.ilike(like)
                | Evidence.source_description.ilike(like)
                | Evidence.notes.ilike(like)
                | Evidence.source_url.ilike(like)
            )
            .order_by(Evidence.created_at.desc())
            .offset(offset)
            .limit(capped)
        )
        return session.exec(stmt).all()
    stmt = select(Evidence).order_by(Evidence.created_at.desc()).offset(offset).limit(capped)
    return session.exec(stmt).all()


@router.get("/{evidence_id}", response_model=EvidenceDetail)
def get_evidence(evidence_id: int, session: Session = Depends(get_session)):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    return evidence


@router.get("/{evidence_id}/entities", response_model=list[LinkedEntityRead])
def evidence_entities(evidence_id: int, session: Session = Depends(get_session)):
    if not session.get(Evidence, evidence_id):
        raise HTTPException(404, "Evidence not found.")
    stmt = (
        select(Entity, EvidenceEntityLink.role)
        .join(EvidenceEntityLink, EvidenceEntityLink.entity_id == Entity.id)
        .where(EvidenceEntityLink.evidence_id == evidence_id)
        .order_by(Entity.name)
    )
    return [
        LinkedEntityRead(id=ent.id, name=ent.name, type=ent.type, role=role)
        for ent, role in session.exec(stmt).all()
    ]


@router.patch("/{evidence_id}", response_model=EvidenceDetail)
def update_metadata(
    evidence_id: int,
    patch: EvidenceMetadata,
    session: Session = Depends(get_session),
):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    changed = patch.model_dump(exclude_unset=True)
    for key, value in changed.items():
        setattr(evidence, key, value)
    session.add(evidence)
    _log(
        session,
        evidence.id,
        CustodyAction.ANNOTATED,
        actor=evidence.collected_by,
        detail=f"Updated metadata: {', '.join(changed) or 'no fields'}",
        hash_at_event=evidence.sha256,
    )
    session.commit()
    session.refresh(evidence)
    return evidence


@router.post("/{evidence_id}/note", response_model=EvidenceDetail)
def add_note(evidence_id: int, note: CustodyNote, session: Session = Depends(get_session)):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    _log(
        session,
        evidence.id,
        CustodyAction.ANNOTATED,
        actor=note.actor,
        detail=note.detail,
        hash_at_event=evidence.sha256,
    )
    session.commit()
    session.refresh(evidence)
    return evidence


@router.post("/{evidence_id}/verify", response_model=VerifyResult)
def verify_evidence(evidence_id: int, session: Session = Depends(get_session)):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")

    intact = storage.verify(evidence.sha256)
    action = CustodyAction.VERIFIED if intact else CustodyAction.VERIFY_FAILED
    message = (
        "Integrity confirmed: stored bytes match the recorded SHA-256."
        if intact
        else "INTEGRITY FAILURE: stored object is missing or altered."
    )
    _log(
        session,
        evidence.id,
        action,
        actor=None,
        detail=message,
        hash_at_event=evidence.sha256,
    )
    session.commit()
    return VerifyResult(
        evidence_id=evidence.id, sha256=evidence.sha256, intact=intact, message=message
    )


@router.get("/{evidence_id}/download")
def download_evidence(evidence_id: int, session: Session = Depends(get_session)):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    path = storage.get_path(evidence.sha256)
    if not path.exists():
        raise HTTPException(410, "Stored object is missing from the vault.")

    _log(
        session,
        evidence.id,
        CustodyAction.EXPORTED,
        actor=None,
        detail="File downloaded.",
        hash_at_event=evidence.sha256,
    )
    session.commit()
    return FileResponse(
        path, media_type=evidence.content_type, filename=evidence.filename
    )
