#!/usr/bin/env python3
"""Migrate generic 'collected.html' filenames to descriptive names based on source URL.

This script updates the 'filename' field in the database for evidence items that
were collected with the old generic naming scheme. It does NOT move or rename
the actual stored files (those are content-addressed by SHA-256 and remain unchanged).

Run from the backend directory:
    python scripts/migrate_filenames.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import get_session
from app.models import Evidence, ChainOfCustodyEvent, CustodyAction
from urllib.parse import urlparse, unquote


def generate_filename_from_url(url: str, content_type: str) -> str:
    """Generate a descriptive filename from URL (same logic as fetcher._filename_from)."""
    path = urlparse(url).path
    if path and "/" in path:
        candidate = unquote(path.rsplit("/", 1)[-1])
        if candidate and "." in candidate:
            return candidate
        if candidate:
            ext = {
                "application/pdf": ".pdf",
                "text/html": ".html",
                "application/json": ".json",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }.get(content_type.split(";")[0].strip(), "")
            return f"{candidate}{ext}" if ext else candidate
    domain = urlparse(url).netloc.replace("www.", "")
    ext = {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "application/json": ".json",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }.get(content_type.split(";")[0].strip(), "")
    return f"{domain}{ext}"


def migrate_filenames(session: Session, dry_run: bool = True) -> None:
    """Update generic filenames to descriptive names."""
    # Find all evidence with generic 'collected.html' or 'collected' filenames
    generic_filenames = ["collected.html", "collected"]
    evidence = session.exec(
        select(Evidence).where(Evidence.filename.in_(generic_filenames))
    ).all()

    print(f"Found {len(evidence)} evidence items with generic filenames")

    for ev in evidence:
        if not ev.source_url:
            print(f"  Skipping ID {ev.id}: no source URL")
            continue

        new_filename = generate_filename_from_url(ev.source_url, ev.content_type)

        if new_filename == ev.filename:
            print(f"  Skipping ID {ev.id}: filename already optimal")
            continue

        print(f"  ID {ev.id}: '{ev.filename}' -> '{new_filename}'")
        print(f"    Source: {ev.source_url}")

        if not dry_run:
            ev.filename = new_filename
            session.add(ev)

            # Log the rename in custody chain
            session.add(
                ChainOfCustodyEvent(
                    evidence_id=ev.id,
                    action=CustodyAction.LINKED,  # Reuse LINKED for metadata updates
                    actor="migration_script",
                    detail=f"Renamed filename from 'collected.html' to '{new_filename}' based on source URL",
                    hash_at_event=ev.sha256,
                )
            )

    if not dry_run:
        session.commit()
        print(f"\nCommitted {len(evidence)} filename updates")
    else:
        print("\nDry run complete. No changes made. Run with --apply to apply changes.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate generic filenames to descriptive names")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()

    session = next(get_session())
    try:
        migrate_filenames(session, dry_run=not args.apply)
    finally:
        session.close()
