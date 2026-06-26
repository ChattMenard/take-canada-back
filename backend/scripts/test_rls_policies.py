#!/usr/bin/env python3
"""Test PostgreSQL Row-Level Security (RLS) policies.

This script verifies that RLS policies correctly prevent unauthorized
DELETE and UPDATE operations on the custody log and evidence tables.
"""

import sys
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from database import get_session
from models import ChainOfCustodyEvent, Evidence
from sqlalchemy import text


def test_rls_policies():
    """Test that RLS policies block forbidden operations."""
    print("Testing PostgreSQL Row-Level Security policies...")
    
    session = next(get_session())
    
    # Test 1: Verify RLS is enabled
    print("\n1. Checking RLS status...")
    result = session.execute(text("""
        SELECT tablename, rowsecurity 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('chainofcustodyevent', 'evidence')
    """))
    rows = result.fetchall()
    
    for table, enabled in rows:
        status = "ENABLED" if enabled else "DISABLED"
        print(f"  {table}: {status}")
        if not enabled:
            print(f"  ❌ RLS not enabled on {table}")
            return False
    
    # Test 2: Try to delete a custody event (should fail)
    print("\n2. Testing DELETE protection on custody events...")
    try:
        # First create a test event
        from custody import create_custody_event
        test_evidence = Evidence(
            sha256="test1234567890abcdef" * 4,
            filename="test.txt",
            content_type="text/plain",
            size_bytes=4,
            title="Test Evidence"
        )
        session.add(test_evidence)
        session.commit()
        
        event = create_custody_event(
            session,
            evidence_id=test_evidence.id,
            action="CREATED",
            actor="test_user",
            detail="Test event for RLS testing",
            hash_at_event=test_evidence.sha256
        )
        event_id = event.id
        
        # Now try to delete it (should fail)
        session.delete(event)
        session.commit()
        print("  ❌ DELETE succeeded - RLS policy not working!")
        return False
        
    except Exception as exc:
        session.rollback()
        print(f"  ✅ DELETE blocked as expected: {exc}")
    
    # Test 3: Try to update a custody event (should fail)
    print("\n3. Testing UPDATE protection on custody events...")
    try:
        event = session.get(ChainOfCustodyEvent, event_id)
        event.detail = "Modified detail"
        session.commit()
        print("  ❌ UPDATE succeeded - RLS policy not working!")
        return False
        
    except Exception as exc:
        session.rollback()
        print(f"  ✅ UPDATE blocked as expected: {exc}")
    
    # Test 4: Try to delete evidence (should fail)
    print("\n4. Testing DELETE protection on evidence...")
    try:
        session.delete(test_evidence)
        session.commit()
        print("  ❌ DELETE succeeded - RLS policy not working!")
        return False
        
    except Exception as exc:
        session.rollback()
        print(f"  ✅ DELETE blocked as expected: {exc}")
    
    # Test 5: Verify INSERT and SELECT still work
    print("\n5. Testing INSERT and SELECT operations...")
    try:
        # INSERT should work
        new_evidence = Evidence(
            sha256="new1234567890abcdef" * 4,
            filename="new.txt",
            content_type="text/plain",
            size_bytes=8,
            title="New Test Evidence"
        )
        session.add(new_evidence)
        session.commit()
        
        # SELECT should work
        evidence = session.get(Evidence, new_evidence.id)
        if evidence and evidence.title == "New Test Evidence":
            print("  ✅ INSERT and SELECT working correctly")
        else:
            print("  ❌ SELECT not working correctly")
            return False
            
    except Exception as exc:
        session.rollback()
        print(f"  ❌ INSERT/SELECT failed: {exc}")
        return False
    
    # Cleanup
    try:
        session.delete(test_evidence)
        session.delete(new_evidence)
        session.commit()
    except Exception:
        session.rollback()
    
    print("\n✅ All RLS policy tests passed!")
    return True


def main():
    """Run RLS policy tests."""
    if not test_rls_policies():
        print("\n❌ RLS policy tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
