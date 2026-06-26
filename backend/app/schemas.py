"""Pydantic DTOs for request/response bodies (kept separate from ORM tables)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: CustodyAction
    actor: str | None
    detail: str | None
    hash_at_event: str | None
    timestamp: datetime


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class LinkedEvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    sha256: str
    role: str | None = None


class LinkedEntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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


# --------------------------- Export ------------------------------ #
class VaultManifest(BaseModel):
    version: str = "1.0"
    generated_at: datetime
    vault_id: str
    seal: dict | None = None
    stats: Stats
    evidence: list[EvidenceRead]
    entities: list[EntityRead]
    relationships: list[RelationshipRead]
    timeline: list[TimelineEventRead]


class ExportResult(BaseModel):
    manifest_path: str
    package_path: str | None = None
    warc_path: str | None = None
    evidence_count: int
    storage_bytes: int


class WarcExportResult(BaseModel):
    warc_path: str
    evidence_count: int
    storage_bytes: int
    warc_bytes: int
