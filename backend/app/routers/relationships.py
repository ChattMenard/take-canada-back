"""Phase 2 foundation — relationships between entities (the collusion graph)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Entity, Relationship_
from ..schemas import RelationshipCreate, RelationshipRead

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.post("", response_model=RelationshipRead, status_code=201)
def create_relationship(payload: RelationshipCreate, session: Session = Depends(get_session)):
    for eid in (payload.source_entity_id, payload.target_entity_id):
        if not session.get(Entity, eid):
            raise HTTPException(422, f"Entity {eid} does not exist.")
    rel = Relationship_(**payload.model_dump())
    session.add(rel)
    session.commit()
    session.refresh(rel)
    return rel


@router.get("", response_model=list[RelationshipRead])
def list_relationships(entity_id: int | None = None, session: Session = Depends(get_session)):
    stmt = select(Relationship_).order_by(Relationship_.created_at.desc())
    if entity_id is not None:
        stmt = stmt.where(
            (Relationship_.source_entity_id == entity_id)
            | (Relationship_.target_entity_id == entity_id)
        )
    return session.exec(stmt).all()


@router.delete("/{relationship_id}", status_code=204)
def delete_relationship(relationship_id: int, session: Session = Depends(get_session)):
    rel = session.get(Relationship_, relationship_id)
    if not rel:
        raise HTTPException(404, "Relationship not found.")
    session.delete(rel)
    session.commit()
