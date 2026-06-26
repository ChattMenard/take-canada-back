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

from sqlmodel import Field, Relationship, SQLModel, Text

# --------------------------------------------------------------------------- #
# Economic evidence models
# --------------------------------------------------------------------------- #
class EconomicIndicator(SQLModel, table=True):
    """Economic indicators tracking wealth gap and business health."""
    
    __tablename__ = "economic_indicators"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    indicator_type: str = Field(index=True)  # "small_business_count", "inflation_rate", "wealth_gap", etc.
    value: float
    source: str
    region: str = Field(default="Canada")
    notes: str | None = Field(default=None, sa_type=Text)


class BusinessMetrics(SQLModel, table=True):
    """Business performance metrics by size and sector."""
    
    __tablename__ = "business_metrics"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    business_size: str = Field(index=True)  # "small", "medium", "large", "corporate"
    sector: str = Field(index=True)
    total_sales: float
    total_profits: float
    operating_expenses: float
    employee_count: int
    closure_rate: float | None = Field(default=None)
    source: str
    region: str = Field(default="Canada")


class PolicyAction(SQLModel, table=True):
    """Government policy actions and their claimed vs. actual impacts."""
    
    __tablename__ = "policy_actions"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    policy_type: str = Field(index=True)  # "inflation", "tax", "regulation", "emergency"
    policy_name: str
    description: str = Field(sa_type=Text)
    claimed_purpose: str = Field(sa_type=Text)  # What government said it would do
    actual_impact: str = Field(sa_type=Text)   # What it actually did
    affected_groups: str = Field(default="all")  # Who was actually affected
    source_url: str | None = Field(default=None)
    source_document: str | None = Field(default=None)


class HypocrisyTracker(SQLModel, table=True):
    """Track government statements vs. their actions that harm citizens."""
    
    __tablename__ = "hypocrisy_tracker"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    official: str = Field(index=True)  # Who made the statement
    statement: str = Field(sa_type=Text)  # What they said
    statement_date: datetime
    contradictory_action: str = Field(sa_type=Text)  # What they actually did
    action_date: datetime
    harm_caused: str = Field(sa_type=Text)  # How it harmed citizens
    evidence_urls: str = Field(default="")  # Comma-separated URLs
    verified: bool = Field(default=False)


class WealthTransfer(SQLModel, table=True):
    """Document specific mechanisms of wealth transfer from citizens to elite."""
    
    __tablename__ = "wealth_transfer"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    mechanism: str = Field(index=True)  # "inflation_tax", "regulatory_capture", "subsidy", etc.
    amount: float  # Estimated amount transferred
    from_group: str  # Who lost wealth (e.g., "small_businesses", "working_class")
    to_group: str   # Who gained wealth (e.g., "corporations", "government")
    method: str = Field(sa_type=Text)  # How the transfer worked
    policy_reference: str | None = Field(default=None)
    evidence_summary: str = Field(sa_type=Text)
    source_urls: str = Field(default="")

# --------------------------------------------------------------------------- #
# Transparency campaign models
# --------------------------------------------------------------------------- #
class EmergencyPower(SQLModel, table=True):
    """Emergency powers usage and Charter rights suspensions."""
    
    __tablename__ = "emergency_powers"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    power_type: str = Field(index=True)  # "emergencies_act", "interim_order", "mandate"
    title: str
    description: str = Field(sa_type=Text)
    legal_basis: str = Field(sa_type=Text)  # Legal authority cited
    rights_suspended: str = Field(sa_type=Text)  # Charter rights affected
    duration: str  # How long it was in effect
    scope: str = Field(default="national")  # Geographic scope
    affected_groups: str = Field(default="all citizens")
    oversight: str = Field(default="none")  # Parliamentary/judicial oversight
    source_url: str | None = Field(default=None)
    source_document: str | None = Field(default=None)


class SurveillanceInfrastructure(SQLModel, table=True):
    """Surveillance infrastructure and data collection programs."""
    
    __tablename__ = "surveillance_infrastructure"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    program_name: str
    agency: str = Field(index=True)  # "CSE", "FINTRAC", "RCMP", etc.
    data_type: str = Field(index=True)  # "financial", "communications", "location", etc.
    legal_authority: str = Field(sa_type=Text)
    collection_method: str = Field(sa_type=Text)
    data_retention: str  # How long data is kept
    access_controls: str = Field(sa_type=Text)
    oversight_mechanism: str = Field(default="none")
    budget_allocated: float | None = Field(default=None)
    effectiveness_claims: str = Field(sa_type=Text)
    privacy_impact: str = Field(sa_type=Text)
    source_url: str | None = Field(default=None)


class FinancialTransparency(SQLModel, table=True):
    """Financial system transparency and central bank operations."""
    
    __tablename__ = "financial_transparency"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    institution: str = Field(index=True)  # "Bank of Canada", "Big Five banks", etc.
    operation_type: str = Field(index=True)  # "QE", "rate_decision", "bailout", etc.
    amount: float | None = Field(default=None)
    description: str = Field(sa_type=Text)
    stated_purpose: str = Field(sa_type=Text)
    actual_impact: str = Field(sa_type=Text)
    beneficiaries: str = Field(sa_type=Text)  # Who actually benefited
    affected_groups: str = Field(sa_type=Text)  # Who was harmed
    transparency_level: str = Field(default="low")  # "high", "medium", "low", "none"
    oversight: str = Field(default="limited")
    source_url: str | None = Field(default=None)


class CivilLibertiesLitigation(SQLModel, table=True):
    """Civil liberties challenges to government overreach."""
    
    __tablename__ = "civil_liberties_litigation"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    case_name: str
    court_level: str = Field(index=True)  # "federal", "provincial", "supreme"
    organization: str = Field(index=True)  # "CCLA", "BCCLA", "Citizen Lab", etc.
    challenged_policy: str = Field(sa_type=Text)
    legal_basis: str = Field(sa_type=Text)  # Charter sections, etc.
    outcome: str = Field(index=True)  # "victory", "defeat", "ongoing", "settled"
    significance: str = Field(sa_type=Text)
    precedent_set: str = Field(sa_type=Text)
    government_response: str = Field(sa_type=Text)
    media_coverage: str = Field(default="limited")  # "extensive", "moderate", "limited", "none"
    source_url: str | None = Field(default=None)


class CharterViolation(SQLModel, table=True):
    """Specific Charter rights violations and their impacts."""
    
    __tablename__ = "charter_violations"
    
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    charter_section: str = Field(index=True)  # "2", "7", "8", "9", "10", "11", etc.
    right_violated: str = Field(index=True)
    violating_policy: str = Field(sa_type=Text)
    violation_mechanism: str = Field(sa_type=Text)
    affected_individuals: str = Field(sa_type=Text)
    duration: str
    remedy_sought: str = Field(sa_type=Text)
    remedy_granted: str = Field(default="none")
    court_challenges: str = Field(default="none")
    ongoing_impact: str = Field(sa_type=Text)
    evidence_sources: str = Field(default="")  # Comma-separated URLs


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
