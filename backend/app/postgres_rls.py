"""PostgreSQL row-level security policies for tamper-evident custody log.

This module defines RLS policies that make unauthorized writes to the 
chain of custody log structurally impossible at the database layer.

These policies should be applied after migrating from SQLite to PostgreSQL.
"""

from typing import List

# RLS policy definitions for ChainOfCustodyEvent table
CUSTODY_RLS_POLICIES = [
    """
    -- Enable RLS on chainofcustodyevent table
    ALTER TABLE chainofcustodyevent ENABLE ROW LEVEL SECURITY;
    """,
    """
    -- Prevent DELETE operations on custody events
    CREATE POLICY prevent_delete ON chainofcustodyevent
    FOR DELETE
    USING (false);
    """,
    """
    -- Prevent UPDATE operations on custody events
    CREATE POLICY prevent_update ON chainofcustodyevent
    FOR UPDATE
    USING (false);
    """,
    """
    -- Allow INSERT operations (for creating new custody events)
    CREATE POLICY allow_insert ON chainofcustodyevent
    FOR INSERT
    WITH CHECK (true);
    """,
    """
    -- Allow SELECT operations (for reading custody events)
    CREATE POLICY allow_select ON chainofcustodyevent
    FOR SELECT
    USING (true);
    """,
]

# RLS policy definitions for Evidence table (prevent deletion)
EVIDENCE_RLS_POLICIES = [
    """
    -- Enable RLS on evidence table
    ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
    """,
    """
    -- Prevent DELETE operations on evidence records
    CREATE POLICY prevent_delete_evidence ON evidence
    FOR DELETE
    USING (false);
    """,
    """
    -- Allow UPDATE operations (for metadata updates)
    CREATE POLICY allow_update_evidence ON evidence
    FOR UPDATE
    USING (true);
    """,
    """
    -- Allow INSERT operations (for creating new evidence)
    CREATE POLICY allow_insert_evidence ON evidence
    FOR INSERT
    WITH CHECK (true);
    """,
    """
    -- Allow SELECT operations (for reading evidence)
    CREATE POLICY allow_select_evidence ON evidence
    FOR SELECT
    USING (true);
    """,
]


def get_rls_migration_sql() -> str:
    """Return the complete SQL for applying RLS policies."""
    all_policies = CUSTODY_RLS_POLICIES + EVIDENCE_RLS_POLICIES
    return "\n".join(all_policies)


def apply_rls_policies(session) -> None:
    """Apply RLS policies to the database.
    
    This should be called after database migration to PostgreSQL.
    """
    from sqlalchemy import text
    
    sql = get_rls_migration_sql()
    
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            try:
                session.execute(text(statement))
                session.commit()
            except Exception as exc:
                session.rollback()
                raise RuntimeError(f"Failed to apply RLS policy: {exc}") from exc
