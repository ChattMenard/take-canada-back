#!/usr/bin/env python3
"""Add prev_hash column to ChainOfCustodyEvent table for hash-chained custody log.

This migration adds the prev_hash column and populates it for existing events
by computing the hash of each event's serialized fields based on the previous
event in the chain.

Run from the backend directory:
    python scripts/migrate_hash_chain.py
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import get_session
from app.models import ChainOfCustodyEvent


def serialize_event(event: ChainOfCustodyEvent) -> str:
    """Serialize a custody event for hashing."""
    # Handle both datetime objects and strings
    timestamp = event.timestamp
    if hasattr(timestamp, "isoformat"):
        timestamp = timestamp.isoformat()
    
    # Handle action enum
    action = event.action
    if hasattr(action, "value"):
        action = action.value
    
    data = {
        "id": event.id,
        "evidence_id": event.evidence_id,
        "action": action,
        "actor": event.actor,
        "detail": event.detail,
        "hash_at_event": event.hash_at_event,
        "timestamp": timestamp,
    }
    return json.dumps(data, sort_keys=True)


def hash_event(event: ChainOfCustodyEvent, prev_hash: str | None = None) -> str:
    """Hash a custody event including the previous event's hash."""
    serialized = serialize_event(event)
    if prev_hash:
        serialized = f"{prev_hash}|{serialized}"
    return hashlib.sha256(serialized.encode()).hexdigest()


def migrate_hash_chain(session: Session, dry_run: bool = True) -> None:
    """Add prev_hash column and populate for existing events."""
    # Check if column exists
    from sqlalchemy import inspect, text
    inspector = inspect(session.bind)
    columns = [col["name"] for col in inspector.get_columns("chainofcustodyevent")]

    if "prev_hash" in columns:
        print("prev_hash column already exists")
    else:
        print("Adding prev_hash column...")
        if not dry_run:
            session.exec(text("ALTER TABLE chainofcustodyevent ADD COLUMN prev_hash TEXT"))
            session.commit()

    # Populate prev_hash for existing events (use raw SQL to avoid model loading issues)
    result = session.exec(
        text("SELECT id, evidence_id, action, actor, detail, hash_at_event, timestamp FROM chainofcustodyevent ORDER BY evidence_id, timestamp")
    ).all()

    # Group by evidence_id
    by_evidence = {}
    for row in result:
        ev_id, evidence_id, action, actor, detail, hash_at_event, timestamp = row
        if evidence_id not in by_evidence:
            by_evidence[evidence_id] = []
        by_evidence[evidence_id].append({
            "id": ev_id,
            "evidence_id": evidence_id,
            "action": action,
            "actor": actor,
            "detail": detail,
            "hash_at_event": hash_at_event,
            "timestamp": timestamp,
        })

    updated = 0
    for evidence_id, ev_list in by_evidence.items():
        prev_hash = None
        for ev in ev_list:
            # Create a simple object for hashing
            class EventProxy:
                def __init__(self, data):
                    self.id = data["id"]
                    self.evidence_id = data["evidence_id"]
                    self.action = data["action"]
                    self.actor = data["actor"]
                    self.detail = data["detail"]
                    self.hash_at_event = data["hash_at_event"]
                    self.timestamp = data["timestamp"]

            proxy = EventProxy(ev)
            computed_hash = hash_event(proxy, prev_hash)
            print(f"  Event {ev['id']} (evidence {evidence_id}): prev_hash = {computed_hash[:16]}...")
            updated += 1
            if not dry_run:
                session.execute(
                    text("UPDATE chainofcustodyevent SET prev_hash = :prev_hash WHERE id = :id"),
                    {"prev_hash": computed_hash, "id": ev["id"]}
                )
            prev_hash = computed_hash
    
    if not dry_run:
        session.commit()
        print(f"\nCommitted {updated} event updates")
    else:
        print(f"\nDry run complete. {updated} events would be updated. Run with --apply to apply changes.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate to hash-chained custody log")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    session = next(get_session())
    try:
        migrate_hash_chain(session, dry_run=not args.apply)
    finally:
        session.close()
