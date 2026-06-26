# PostgreSQL Migration Guide

This guide explains how to migrate Veritas from SQLite to PostgreSQL with row-level security (RLS) for enhanced tamper-evidence.

## Why PostgreSQL?

PostgreSQL provides:

- **Row-Level Security (RLS)**: Makes unauthorized writes to the custody log structurally impossible at the database layer
- **Concurrent write support**: Better performance for multi-user environments
- **ACID compliance**: Strong data integrity guarantees
- **Audit triggers**: Built-in audit logging capabilities

## Prerequisites

1. PostgreSQL 14+ installed and running
2. Database created: `createdb veritas`
3. Environment variables set:
   ```bash
   export VERITAS_DATABASE_URL="postgresql://user:password@localhost/veritas"
   ```

## Migration Steps

### 1. Install PostgreSQL dependencies

```bash
cd backend
pip install psycopg2-binary
```

### 2. Set database URL

```bash
export VERITAS_DATABASE_URL="postgresql://veritas:yourpassword@localhost/veritas"
```

Or add to `.env` file:

```
VERITAS_DATABASE_URL=postgresql://veritas:yourpassword@localhost/veritas
```

## 3. Run database initialization

```bash
python -c "from app.database import init_db; init_db()"
```

This will create all tables using PostgreSQL.

### 4. Apply Row-Level Security policies

```python
from app.postgres_rls import apply_rls_policies
from app.database import get_session

session = next(get_session())
apply_rls_policies(session)
```

Or run the migration script:

```bash
python scripts/migrate_postgres_rls.py
```

## 5. Verify RLS is active

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('chainofcustodyevent', 'evidence');

-- Check policies exist
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('chainofcustodyevent', 'evidence');
```

## RLS Policies Applied

### ChainOfCustodyEvent
- **DELETE**: Blocked (using `false`)
- **UPDATE**: Blocked (using `false`)
- **INSERT**: Allowed (using `true`)
- **SELECT**: Allowed (using `true`)

### Evidence
- **DELETE**: Blocked (using `false`)
- **UPDATE**: Allowed (for metadata updates)
- **INSERT**: Allowed (for new evidence)
- **SELECT**: Allowed (for reading)

## Rollback

To disable RLS (not recommended in production):

```sql
ALTER TABLE chainofcustodyevent DISABLE ROW LEVEL SECURITY;
ALTER TABLE evidence DISABLE ROW LEVEL SECURITY;
```

To drop policies:

```sql
DROP POLICY IF EXISTS prevent_delete ON chainofcustodyevent;
DROP POLICY IF EXISTS prevent_update ON chainofcustodyevent;
DROP POLICY IF EXISTS allow_insert ON chainofcustodyevent;
DROP POLICY IF EXISTS allow_select ON chainofcustodyevent;
DROP POLICY IF EXISTS prevent_delete_evidence ON evidence;
DROP POLICY IF EXISTS allow_update_evidence ON evidence;
DROP POLICY IF EXISTS allow_insert_evidence ON evidence;
DROP POLICY IF EXISTS allow_select_evidence ON evidence;
```

## Performance Considerations

PostgreSQL with RLS has minimal performance overhead. For high-volume deployments:

- Use connection pooling (PgBouncer)
- Enable statement logging for audit trails
- Consider partitioning for large evidence tables
- Regular VACUUM and ANALYZE maintenance

## Security Benefits

1. **Defense in depth**: RLS provides database-layer protection even if application authentication is bypassed
2. **Immutable audit trail**: Custody events cannot be deleted or modified at the database level
3. **Compliance**: Meets evidentiary standards for forensic investigations
4. **Tamper evidence**: Any attempt to bypass RLS will be logged in PostgreSQL logs
