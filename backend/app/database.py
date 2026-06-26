from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, text

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)

_FTS_SETUP = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts
    USING fts5(
        title,
        source_description,
        notes,
        extracted_text,
        content='evidence',
        content_rowid='id'
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS evidence_fts_insert
    AFTER INSERT ON evidence BEGIN
        INSERT INTO evidence_fts(rowid, title, source_description, notes, extracted_text)
        VALUES (new.id, new.title, new.source_description, new.notes, new.extracted_text);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS evidence_fts_update
    AFTER UPDATE ON evidence BEGIN
        INSERT INTO evidence_fts(evidence_fts, rowid, title, source_description, notes, extracted_text)
        VALUES ('delete', old.id, old.title, old.source_description, old.notes, old.extracted_text);
        INSERT INTO evidence_fts(rowid, title, source_description, notes, extracted_text)
        VALUES (new.id, new.title, new.source_description, new.notes, new.extracted_text);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS evidence_fts_delete
    AFTER DELETE ON evidence BEGIN
        INSERT INTO evidence_fts(evidence_fts, rowid, title, source_description, notes, extracted_text)
        VALUES ('delete', old.id, old.title, old.source_description, old.notes, old.extracted_text);
    END
    """,
]


def _is_sqlite() -> bool:
    return settings.database_url.startswith("sqlite")


def init_db() -> None:
    # Import models so SQLModel registers every table before create_all.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)

    if _is_sqlite():
        with engine.connect() as conn:
            for stmt in _FTS_SETUP:
                conn.execute(text(stmt))
            conn.commit()
    else:
        # PostgreSQL: apply Row-Level Security policies for tamper-evidence
        try:
            from .postgres_rls import apply_rls_policies
            with Session(engine) as session:
                apply_rls_policies(session)
                print("PostgreSQL RLS policies applied")
        except Exception as exc:
            print(f"Warning: Failed to apply PostgreSQL RLS policies: {exc}")
            print("Run 'python scripts/migrate_postgres_rls.py' manually to apply them")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
