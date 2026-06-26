#!/usr/bin/env python3
"""Apply PostgreSQL Row-Level Security (RLS) policies to Veritas database.

Run this after migrating to PostgreSQL to enable append-only custody log
and tamper-evident evidence records.
"""

import sys
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from database import get_session
from postgres_rls import apply_rls_policies


def main():
    """Apply RLS policies to the database."""
    print("Applying PostgreSQL Row-Level Security policies...")
    
    try:
        session = next(get_session())
        apply_rls_policies(session)
        print("✅ RLS policies applied successfully!")
        
        # Verify policies were applied
        from sqlalchemy import text
        result = session.execute(text("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('chainofcustodyevent', 'evidence')
        """))
        rows = result.fetchall()
        print("\nRLS status:")
        for table, enabled in rows:
            status = "ENABLED" if enabled else "DISABLED"
            print(f"  {table}: {status}")
        
        # List policies
        result = session.execute(text("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd 
            FROM pg_policies 
            WHERE tablename IN ('chainofcustodyevent', 'evidence')
            ORDER BY tablename, policyname
        """))
        policies = result.fetchall()
        if policies:
            print("\nPolicies applied:")
            for schema, table, name, permissive, roles, cmd in policies:
                print(f"  {table}.{name} ({cmd})")
        else:
            print("\n⚠️  No policies found - RLS may not be properly enabled")
            
    except Exception as exc:
        print(f"❌ Failed to apply RLS policies: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
