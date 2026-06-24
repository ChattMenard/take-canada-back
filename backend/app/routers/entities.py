"""Phase 2 foundation — entities (people, banks, agencies, companies)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Entity, EvidenceEntityLink
from ..schemas import EntityCreate, EntityRead

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.post("", response_model=EntityRead, status_code=201)
def create_entity(payload: EntityCreate, session: Session = Depends(get_session)):
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
    link = EvidenceEntityLink(evidence_id=evidence_id, entity_id=entity_id, role=role)
    session.merge(link)
    session.commit()
    return {"evidence_id": evidence_id, "entity_id": entity_id, "role": role}
