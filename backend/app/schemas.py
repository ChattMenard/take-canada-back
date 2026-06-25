"""Pydantic DTOs for request/response bodies (kept separate from ORM tables)."""

from datetime import datetime

from pydantic import BaseModel

from .models import CustodyAction, EntityType, RelationshipKind


# --------------------------- Evidence --------------------------- #
class EvidenceMetadata(BaseModel):
    title: str | None = None
    source_url: str | None = None
    source_description: str | None = None
    captured_at: datetime | None = None
    collected_by: str | None = None
    notes: str | None = None


class CustodyEventRead(BaseModel):
    id: int
    action: CustodyAction
    actor: str | None
    detail: str | None
    hash_at_event: str | None
    timestamp: datetime


class EvidenceRead(BaseModel):
    id: int
    sha256: str
    title: str
    filename: str
    content_type: str
    size_bytes: int
    source_url: str | None
    source_description: str | None
    captured_at: datetime | None
    collected_by: str | None
    notes: str | None
    created_at: datetime


class EvidenceDetail(EvidenceRead):
    custody_events: list[CustodyEventRead] = []


class VerifyResult(BaseModel):
    evidence_id: int
    sha256: str
    intact: bool
    message: str


class CustodyNote(BaseModel):
    actor: str | None = None
    detail: str


class UrlCollect(BaseModel):
    url: str
    title: str | None = None
    source_description: str | None = None
    captured_at: datetime | None = None
    collected_by: str | None = None
    notes: str | None = None


# --------------------------- Entities --------------------------- #
class EntityCreate(BaseModel):
    name: str
    type: EntityType = EntityType.OTHER
    description: str | None = None


class EntityRead(EntityCreate):
    id: int
    created_at: datetime


class LinkedEvidenceRead(BaseModel):
    id: int
    title: str
    sha256: str
    role: str | None = None


class LinkedEntityRead(BaseModel):
    id: int
    name: str
    type: EntityType
    role: str | None = None


# ------------------------ Relationships ------------------------- #
class RelationshipCreate(BaseModel):
    source_entity_id: int
    target_entity_id: int
    kind: RelationshipKind = RelationshipKind.OTHER
    description: str | None = None
    amount: float | None = None
    occurred_at: datetime | None = None


class RelationshipRead(RelationshipCreate):
    id: int
    created_at: datetime
    linked_evidence: list[LinkedEvidenceRead] = []


# -------------------------- Timeline ---------------------------- #
class TimelineEventCreate(BaseModel):
    title: str
    description: str | None = None
    occurred_at: datetime
    evidence_id: int | None = None


class TimelineEventPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    occurred_at: datetime | None = None
    evidence_id: int | None = None


class TimelineEventRead(TimelineEventCreate):
    id: int
    created_at: datetime


# --------------------------- Stats ------------------------------ #
class Stats(BaseModel):
    evidence_count: int
    entity_count: int
    relationship_count: int
    timeline_count: int
    storage_bytes: int


# ------------------------ Timestamping -------------------------- #
class TimestampStatus(BaseModel):
    evidence_id: int
    sha256: str
    timestamped: bool


class TimestampVerifyResult(BaseModel):
    evidence_id: int
    sha256: str
    verified: bool
    pending: bool
    attestations: list[dict] = []
    block_height: int | None = None
    block_hash: str | None = None
    error: str | None = None


class RFC3161Status(BaseModel):
    evidence_id: int
    sha256: str
    timestamped: bool
    verified: bool = False
    error: str | None = None
