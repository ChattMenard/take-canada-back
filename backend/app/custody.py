"""Custody log utilities for hash-chained chain of custody."""

import hashlib
import json
from datetime import datetime, timezone
from sqlmodel import Session, select

from .models import ChainOfCustodyEvent, CustodyAction


def serialize_event(event: ChainOfCustodyEvent) -> str:
    """Serialize a custody event for hashing."""
    data = {
        "id": event.id,
        "evidence_id": event.evidence_id,
        "action": event.action.value if hasattr(event.action, "value") else event.action,
        "actor": event.actor,
        "detail": event.detail,
        "hash_at_event": event.hash_at_event,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
    }
    return json.dumps(data, sort_keys=True)


def hash_event(event: ChainOfCustodyEvent, prev_hash: str | None = None) -> str:
    """Hash a custody event including the previous event's hash."""
    serialized = serialize_event(event)
    if prev_hash:
        serialized = f"{prev_hash}|{serialized}"
    return hashlib.sha256(serialized.encode()).hexdigest()


def get_last_event_hash(session: Session, evidence_id: int) -> str | None:
    """Get the hash of the most recent custody event for an evidence item."""
    last_event = session.exec(
        select(ChainOfCustodyEvent)
        .where(ChainOfCustodyEvent.evidence_id == evidence_id)
        .order_by(ChainOfCustodyEvent.timestamp.desc())
        .limit(1)
    ).first()
    
    if not last_event:
        return None
    
    return hash_event(last_event, last_event.prev_hash)


def create_custody_event(
    session: Session,
    evidence_id: int,
    action: CustodyAction,
    actor: str | None = None,
    detail: str | None = None,
    hash_at_event: str | None = None,
) -> ChainOfCustodyEvent:
    """Create a new custody event with hash-chaining."""
    prev_hash = get_last_event_hash(session, evidence_id)
    
    event = ChainOfCustodyEvent(
        evidence_id=evidence_id,
        action=action,
        actor=actor,
        detail=detail,
        hash_at_event=hash_at_event,
        prev_hash=prev_hash,
    )
    
    session.add(event)
    session.flush()
    session.refresh(event)
    
    return event
