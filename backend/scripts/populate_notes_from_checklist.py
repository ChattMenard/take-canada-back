#!/usr/bin/env python3
"""Populate evidence notes from EVIDENCE_COLLECTION.md checklist.

This script reads the evidence collection checklist and maps URLs to their
legal relevance and threat descriptions, then updates the notes field for
matching evidence items in the vault.

Run from the backend directory:
    python scripts/populate_notes_from_checklist.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import get_session
from app.models import Evidence, ChainOfCustodyEvent, CustodyAction


def parse_checklist(checklist_path: Path) -> dict[str, str]:
    """Parse EVIDENCE_COLLECTION.md and return URL -> notes mapping."""
    content = checklist_path.read_text()
    
    # Split by category headers
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    
    url_to_notes = {}
    current_threat = ""
    current_relevance = ""
    
    for section in sections[1:]:  # Skip intro
        lines = section.split('\n')
        category_header = lines[0] if lines else ""
        
        # Extract threat and relevance sections
        for i, line in enumerate(lines):
            if line.startswith("**Threat:**"):
                current_threat = line.replace("**Threat:**", "").strip()
            elif line.startswith("**Legal relevance:**"):
                # Relevance may span multiple lines
                relevance_lines = [line.replace("**Legal relevance:**", "").strip()]
                j = i + 1
                while j < len(lines) and not lines[j].startswith("|") and not lines[j].startswith("**"):
                    relevance_lines.append(lines[j].strip())
                    j += 1
                current_relevance = " ".join(relevance_lines)
        
        # Extract table rows with URLs (plain URLs in table, not markdown links)
        table_pattern = re.compile(r'\|\s*\d+\.\d+\s*\|\s*([^\|]+)\s*\|\s*(https?://[^\s\|]+)')
        for match in table_pattern.finditer(section):
            doc_name = match.group(1).strip()
            url = match.group(2).strip()
            
            # Build notes from threat + relevance
            notes = f"Threat: {current_threat}\nLegal relevance: {current_relevance}" if current_threat or current_relevance else ""
            
            if url and notes:
                url_to_notes[url] = notes
    
    return url_to_notes


def populate_notes(session: Session, dry_run: bool = True) -> None:
    """Update evidence notes from checklist mapping."""
    checklist_path = Path(__file__).parent.parent.parent / "docs" / "EVIDENCE_COLLECTION.md"
    if not checklist_path.exists():
        print(f"Checklist not found at {checklist_path}")
        return
    
    url_to_notes = parse_checklist(checklist_path)
    print(f"Parsed {len(url_to_notes)} URL mappings from checklist")
    
    # Find evidence with matching source URLs
    evidence = session.exec(select(Evidence)).all()
    
    updated = 0
    for ev in evidence:
        if not ev.source_url:
            continue

        # Direct URL match
        if ev.source_url in url_to_notes:
            notes = url_to_notes[ev.source_url]
            if ev.notes != notes:
                print(f"  ID {ev.id}: Updating notes for {ev.source_url}")
                updated += 1
                if not dry_run:
                    ev.notes = notes
                    session.add(ev)
                    session.add(
                        ChainOfCustodyEvent(
                            evidence_id=ev.id,
                            action=CustodyAction.LINKED,
                            actor="populate_notes_script",
                            detail="Populated notes from EVIDENCE_COLLECTION.md",
                            hash_at_event=ev.sha256,
                        )
                    )
        # Partial match (same domain/path)
        else:
            for checklist_url, notes in url_to_notes.items():
                if ev.source_url.startswith(checklist_url) or checklist_url.startswith(ev.source_url):
                    if ev.notes != notes:
                        print(f"  ID {ev.id}: Partial match - {ev.source_url} -> {checklist_url}")
                        updated += 1
                        if not dry_run:
                            ev.notes = notes
                            session.add(ev)
                            session.add(
                                ChainOfCustodyEvent(
                                    evidence_id=ev.id,
                                    action=CustodyAction.LINKED,
                                    actor="populate_notes_script",
                                    detail=f"Populated notes from EVIDENCE_COLLECTION.md (partial URL match to {checklist_url})",
                                    hash_at_event=ev.sha256,
                                )
                            )
                    break
    
    if not dry_run:
        session.commit()
        print(f"\nCommitted {updated} note updates")
    else:
        print(f"\nDry run complete. {updated} items would be updated. Run with --apply to apply changes.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate evidence notes from checklist")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    session = next(get_session())
    try:
        populate_notes(session, dry_run=not args.apply)
    finally:
        session.close()
