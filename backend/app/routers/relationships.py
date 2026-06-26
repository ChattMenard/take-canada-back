"""Phase 2 foundation — relationships between entities (the collusion graph)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .. import custody
from ..database import get_session
from ..models import Entity, Relationship_, Evidence, EvidenceRelationshipLink, ChainOfCustodyEvent, CustodyAction
from ..routers.seal import ensure_unsealed
from ..schemas import RelationshipCreate, RelationshipRead, LinkedEvidenceRead

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.post("", response_model=RelationshipRead, status_code=201)
def create_relationship(payload: RelationshipCreate, session: Session = Depends(get_session)):
    ensure_unsealed()
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
    ensure_unsealed()
    rel = session.get(Relationship_, relationship_id)
    if not rel:
        raise HTTPException(404, "Relationship not found.")
    session.delete(rel)
    session.commit()


@router.post("/{relationship_id}/link/{evidence_id}", status_code=201)
def link_evidence(
    relationship_id: int,
    evidence_id: int,
    session: Session = Depends(get_session),
):
    ensure_unsealed()
    rel = session.get(Relationship_, relationship_id)
    if not rel:
        raise HTTPException(404, "Relationship not found.")
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    link = EvidenceRelationshipLink(relationship_id=relationship_id, evidence_id=evidence_id)
    session.merge(link)
    # Linking is custody-relevant: record it on the evidence's chain of custody
    custody.create_custody_event(
        session,
        evidence_id=evidence_id,
        action=CustodyAction.LINKED,
        detail=f"Linked to relationship {relationship_id}",
        hash_at_event=evidence.sha256,
    )
    session.commit()
    return {"relationship_id": relationship_id, "evidence_id": evidence_id}


@router.delete("/{relationship_id}/link/{evidence_id}", status_code=204)
def unlink_evidence(
    relationship_id: int,
    evidence_id: int,
    session: Session = Depends(get_session),
):
    ensure_unsealed()
    rel = session.get(Relationship_, relationship_id)
    if not rel:
        raise HTTPException(404, "Relationship not found.")
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found.")
    link = session.exec(
        select(EvidenceRelationshipLink).where(
            EvidenceRelationshipLink.relationship_id == relationship_id,
            EvidenceRelationshipLink.evidence_id == evidence_id,
        )
    ).first()
    if link:
        session.delete(link)
        session.commit()

