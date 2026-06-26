"""Phase 3 foundation — chronological timeline of events."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import TimelineEvent
from ..routers.auth import get_current_admin
from ..routers.seal import ensure_unsealed
from ..schemas import TimelineEventCreate, TimelineEventPatch, TimelineEventRead

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.post("", response_model=TimelineEventRead, status_code=201)
def create_event(
    payload: TimelineEventCreate,
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    ensure_unsealed()
    event = TimelineEvent(**payload.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.get("", response_model=list[TimelineEventRead])
def list_events(session: Session = Depends(get_session)):
    stmt = select(TimelineEvent).order_by(TimelineEvent.occurred_at)
    return session.exec(stmt).all()


@router.patch("/{event_id}", response_model=TimelineEventRead)
def update_event(
    event_id: int,
    patch: TimelineEventPatch,
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    ensure_unsealed()
    event = session.get(TimelineEvent, event_id)
    if not event:
        raise HTTPException(404, "Timeline event not found.")
    for key, value in patch.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    session: Session = Depends(get_session),
    admin: str = Depends(get_current_admin),
):
    ensure_unsealed()
    event = session.get(TimelineEvent, event_id)
    if not event:
        raise HTTPException(404, "Timeline event not found.")
    session.delete(event)
    session.commit()
