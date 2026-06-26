"""Database models for the Veritas evidentiary collection engine.

Architecture spans all three phases:
  * Phase 1 (implemented): Evidence + ChainOfCustodyEvent  -> the vault.
  * Phase 2 (foundation):  Entity + Relationship           -> the graph.
  * Phase 3 (foundation):  TimelineEvent + full-text search -> the archive.

Link tables connect evidence to entities, relationships, and timeline events
so a single source document can substantiate many claims.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class CustodyAction(str, Enum):
    CREATED = "CREATED"
    ACCESSED = "ACCESSED"
    VERIFIED = "VERIFIED"
    VERIFY_FAILED = "VERIFY_FAILED"
    EXPORTED = "EXPORTED"
    ANNOTATED = "ANNOTATED"
    LINKED = "LINKED"


class EntityType(str, Enum):
    PERSON = "PERSON"
    BANK = "BANK"
    AGENCY = "AGENCY"
    COMPANY = "COMPANY"
    OTHER = "OTHER"


class RelationshipKind(str, Enum):
    DONATION = "DONATION"
    CONTRACT = "CONTRACT"
    BOARD_SEAT = "BOARD_SEAT"
    OWNERSHIP = "OWNERSHIP"
    LOBBYING = "LOBBYING"
    EMPLOYMENT = "EMPLOYMENT"
    OTHER = "OTHER"


# --------------------------------------------------------------------------- #
# Link tables
# --------------------------------------------------------------------------- #
class EvidenceEntityLink(SQLModel, table=True):
    evidence_id: int | None = Field(default=None, foreign_key="evidence.id", primary_key=True)
    entity_id: int | None = Field(default=None, foreign_key="entity.id", primary_key=True)
    role: str | None = Field(default=None, description="How the entity figures in this evidence")


class EvidenceRelationshipLink(SQLModel, table=True):
    evidence_id: int | None = Field(default=None, foreign_key="evidence.id", primary_key=True)
    relationship_id: int | None = Field(
        default=None, foreign_key="relationship.id", primary_key=True
    )


# --------------------------------------------------------------------------- #
# Phase 1 — Evidence vault
# --------------------------------------------------------------------------- #
class Evidence(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sha256: str = Field(index=True, description="SHA-256 of the stored bytes (integrity anchor)")
    title: str = Field(index=True)
    filename: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0

    # Provenance
    source_url: str | None = Field(default=None, index=True)
    source_description: str | None = None
    captured_at: datetime | None = Field(
        default=None, description="When the source material was originally captured/published"
    )
    collected_by: str | None = Field(default=None, description="Person/handle who collected it")
    notes: str | None = None
    extracted_text: str | None = Field(default=None, sa_column_kwargs={"info": {"exclude_from_fts": False}})

    created_at: datetime = Field(default_factory=utcnow, index=True)

    custody_events: list["ChainOfCustodyEvent"] = Relationship(
        back_populates="evidence",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "ChainOfCustodyEvent.timestamp"},
    )
    timeline_events: list["TimelineEvent"] = Relationship(back_populates="evidence")
    relationships: list["Relationship_"] = Relationship(
        back_populates="linked_evidence",
        link_model=EvidenceRelationshipLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ChainOfCustodyEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    evidence_id: int = Field(foreign_key="evidence.id", index=True)
    action: CustodyAction
    actor: str | None = Field(default=None, description="Who performed the action")
    detail: str | None = None
    hash_at_event: str | None = Field(default=None, description="Digest observed at event time")
    prev_hash: str | None = Field(default=None, description="Hash of previous custody event in chain (for tamper-evidence)")
    timestamp: datetime = Field(default_factory=utcnow, index=True)

    evidence: Evidence | None = Relationship(back_populates="custody_events")


# --------------------------------------------------------------------------- #
# Phase 2 — Entity & relationship graph (foundation)
# --------------------------------------------------------------------------- #
class Entity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: EntityType = EntityType.OTHER
    description: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class Relationship_(SQLModel, table=True):
    __tablename__ = "relationship"

    id: int | None = Field(default=None, primary_key=True)
    source_entity_id: int = Field(foreign_key="entity.id", index=True)
    target_entity_id: int = Field(foreign_key="entity.id", index=True)
    kind: RelationshipKind = RelationshipKind.OTHER
    description: str | None = None
    amount: float | None = Field(default=None, description="Monetary value, if applicable")
    occurred_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)

    linked_evidence: list["Evidence"] = Relationship(
        back_populates="relationships",
        link_model=EvidenceRelationshipLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# --------------------------------------------------------------------------- #
# Phase 3 — Timeline (foundation)
# --------------------------------------------------------------------------- #
class TimelineEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    occurred_at: datetime = Field(index=True)
    evidence_id: int | None = Field(default=None, foreign_key="evidence.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)

    evidence: Evidence | None = Relationship(back_populates="timeline_events")
