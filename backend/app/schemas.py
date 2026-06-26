"""Pydantic DTOs for request/response bodies (kept separate from ORM tables)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .models import (
    CustodyAction, EntityType, RelationshipKind,
    EconomicIndicator, BusinessMetrics, PolicyAction, HypocrisyTracker, WealthTransfer,
    EmergencyPower, SurveillanceInfrastructure, FinancialTransparency,
    CivilLibertiesLitigation, CharterViolation
)


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


# --------------------------- Economic Evidence --------------------------- #
class EconomicIndicatorBase(BaseModel):
    date: datetime
    indicator_type: str
    value: float
    source: str
    region: str = "Canada"
    notes: str | None = None


class EconomicIndicatorCreate(EconomicIndicatorBase):
    pass


class EconomicIndicatorRead(EconomicIndicatorBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class BusinessMetricsBase(BaseModel):
    date: datetime
    business_size: str
    sector: str
    total_sales: float
    total_profits: float
    operating_expenses: float
    employee_count: int
    closure_rate: float | None = None
    source: str
    region: str = "Canada"


class BusinessMetricsCreate(BusinessMetricsBase):
    pass


class BusinessMetricsRead(BusinessMetricsBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class PolicyActionBase(BaseModel):
    date: datetime
    policy_type: str
    policy_name: str
    description: str
    claimed_purpose: str
    actual_impact: str
    affected_groups: str = "all"
    source_url: str | None = None
    source_document: str | None = None


class PolicyActionCreate(PolicyActionBase):
    pass


class PolicyActionRead(PolicyActionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class HypocrisyTrackerBase(BaseModel):
    date: datetime
    official: str
    statement: str
    statement_date: datetime
    contradictory_action: str
    action_date: datetime
    harm_caused: str
    evidence_urls: str = ""
    verified: bool = False


class HypocrisyTrackerCreate(HypocrisyTrackerBase):
    pass


class HypocrisyTrackerRead(HypocrisyTrackerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class WealthTransferBase(BaseModel):
    date: datetime
    mechanism: str
    amount: float
    from_group: str
    to_group: str
    method: str
    policy_reference: str | None = None
    evidence_summary: str
    source_urls: str = ""


class WealthTransferCreate(WealthTransferBase):
    pass


class WealthTransferRead(WealthTransferBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


# --------------------------- Transparency Campaign --------------------------- #
class EmergencyPowerBase(BaseModel):
    date: datetime
    power_type: str
    title: str
    description: str
    legal_basis: str
    rights_suspended: str
    duration: str
    scope: str = "national"
    affected_groups: str = "all citizens"
    oversight: str = "none"
    source_url: str | None = None
    source_document: str | None = None


class EmergencyPowerCreate(EmergencyPowerBase):
    pass


class EmergencyPowerRead(EmergencyPowerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class SurveillanceInfrastructureBase(BaseModel):
    date: datetime
    program_name: str
    agency: str
    data_type: str
    legal_authority: str
    collection_method: str
    data_retention: str
    access_controls: str
    oversight_mechanism: str = "none"
    budget_allocated: float | None = None
    effectiveness_claims: str
    privacy_impact: str
    source_url: str | None = None


class SurveillanceInfrastructureCreate(SurveillanceInfrastructureBase):
    pass


class SurveillanceInfrastructureRead(SurveillanceInfrastructureBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class FinancialTransparencyBase(BaseModel):
    date: datetime
    institution: str
    operation_type: str
    amount: float | None = None
    description: str
    stated_purpose: str
    actual_impact: str
    beneficiaries: str
    affected_groups: str
    transparency_level: str = "low"
    oversight: str = "limited"
    source_url: str | None = None


class FinancialTransparencyCreate(FinancialTransparencyBase):
    pass


class FinancialTransparencyRead(FinancialTransparencyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class CivilLibertiesLitigationBase(BaseModel):
    date: datetime
    case_name: str
    court_level: str
    organization: str
    challenged_policy: str
    legal_basis: str
    outcome: str
    significance: str
    precedent_set: str
    government_response: str
    media_coverage: str = "limited"
    source_url: str | None = None


class CivilLibertiesLitigationCreate(CivilLibertiesLitigationBase):
    pass


class CivilLibertiesLitigationRead(CivilLibertiesLitigationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class CharterViolationBase(BaseModel):
    date: datetime
    charter_section: str
    right_violated: str
    violating_policy: str
    violation_mechanism: str
    affected_individuals: str
    duration: str
    remedy_sought: str
    remedy_granted: str = "none"
    court_challenges: str = "none"
    ongoing_impact: str
    evidence_sources: str = ""


class CharterViolationCreate(CharterViolationBase):
    pass


class CharterViolationRead(CharterViolationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
