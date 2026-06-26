"""Phase 2 foundation — entities (people, banks, agencies, companies)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .. import custody
from ..database import get_session
from ..models import (
    ChainOfCustodyEvent,
    CustodyAction,
    Entity,
    Evidence,
    EvidenceEntityLink,
)
from ..routers.seal import ensure_unsealed
from ..schemas import EntityCreate, EntityRead, LinkedEvidenceRead

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.post("", response_model=EntityRead, status_code=201)
def create_entity(payload: EntityCreate, session: Session = Depends(get_session)):
    ensure_unsealed()
    entity = Entity(**payload.model_dump())
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


@router.get("", response_model=list[EntityRead])
def list_entities(q: str | None = None, session: Session = Depends(get_session)):
    stmt = select(Entity).order_by(Entity.name)
    if q:
        stmt = stmt.where(Entity.name.ilike(f"%{q}%"))
    return session.exec(stmt).all()


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: int, session: Session = Depends(get_session)):
    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found.")
    return entity


@router.delete("/{entity_id}", status_code=204)
def delete_entity(entity_id: int, session: Session = Depends(get_session)):
    ensure_unsealed()
    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found.")
    session.delete(entity)
    session.commit()


@router.post("/{entity_id}/link/{evidence_id}", status_code=201)
def link_evidence(
    entity_id: int,
    evidence_id: int,
    role: str | None = None,
    session: Session = Depends(get_session),
):
    ensure_unsealed()
    entity = session.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found.")
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")

    link = EvidenceEntityLink(evidence_id=evidence_id, entity_id=entity_id, role=role)
    session.merge(link)
    # Linking is custody-relevant: record it on the evidence's chain of custody.
    custody.create_custody_event(
        session,
        evidence_id=evidence_id,
        action=CustodyAction.LINKED,
        detail=(
            f"Linked to entity '{entity.name}' ({entity.type.value})"
            + (f" as {role}" if role else "")
        ),
        hash_at_event=evidence.sha256,
    )
    session.commit()
    return {"evidence_id": evidence_id, "entity_id": entity_id, "role": role}


@router.delete("/{entity_id}/link/{evidence_id}", status_code=204)
def unlink_evidence(
    entity_id: int, evidence_id: int, session: Session = Depends(get_session)
):
    ensure_unsealed()
    link = session.get(EvidenceEntityLink, (evidence_id, entity_id))
    if link:
        session.delete(link)
        session.commit()


@router.get("/{entity_id}/evidence", response_model=list[LinkedEvidenceRead])
def entity_evidence(entity_id: int, session: Session = Depends(get_session)):
    if not session.get(Entity, entity_id):
        raise HTTPException(404, "Entity not found.")
    stmt = (
        select(Evidence, EvidenceEntityLink.role)
        .join(EvidenceEntityLink, EvidenceEntityLink.evidence_id == Evidence.id)
        .where(EvidenceEntityLink.entity_id == entity_id)
        .order_by(Evidence.created_at.desc())
    )
    return [
        LinkedEvidenceRead(id=ev.id, title=ev.title, sha256=ev.sha256, role=role)
        for ev, role in session.exec(stmt).all()
    ]
