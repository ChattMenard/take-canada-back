"""Transparency campaign evidence models for tracking government accountability."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Text


class EmergencyPower(SQLModel, table=True):
    """Emergency powers usage and Charter rights suspensions."""
    
    __tablename__ = "emergency_powers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
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
    source_url: Optional[str] = Field(default=None)
    source_document: Optional[str] = Field(default=None)


class SurveillanceInfrastructure(SQLModel, table=True):
    """Surveillance infrastructure and data collection programs."""
    
    __tablename__ = "surveillance_infrastructure"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    program_name: str
    agency: str = Field(index=True)  # "CSE", "FINTRAC", "RCMP", etc.
    data_type: str = Field(index=True)  # "financial", "communications", "location", etc.
    legal_authority: str = Field(sa_type=Text)
    collection_method: str = Field(sa_type=Text)
    data_retention: str  # How long data is kept
    access_controls: str = Field(sa_type=Text)
    oversight_mechanism: str = Field(default="none")
    budget_allocated: Optional[float] = Field(default=None)
    effectiveness_claims: str = Field(sa_type=Text)
    privacy_impact: str = Field(sa_type=Text)
    source_url: Optional[str] = Field(default=None)


class FinancialTransparency(SQLModel, table=True):
    """Financial system transparency and central bank operations."""
    
    __tablename__ = "financial_transparency"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    institution: str = Field(index=True)  # "Bank of Canada", "Big Five banks", etc.
    operation_type: str = Field(index=True)  # "QE", "rate_decision", "bailout", etc.
    amount: Optional[float] = Field(default=None)
    description: str = Field(sa_type=Text)
    stated_purpose: str = Field(sa_type=Text)
    actual_impact: str = Field(sa_type=Text)
    beneficiaries: str = Field(sa_type=Text)  # Who actually benefited
    affected_groups: str = Field(sa_type=Text)  # Who was harmed
    transparency_level: str = Field(default="low")  # "high", "medium", "low", "none"
    oversight: str = Field(default="limited")
    source_url: Optional[str] = Field(default=None)


class CivilLibertiesLitigation(SQLModel, table=True):
    """Civil liberties challenges to government overreach."""
    
    __tablename__ = "civil_liberties_litigation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
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
    source_url: Optional[str] = Field(default=None)


class CharterViolation(SQLModel, table=True):
    """Specific Charter rights violations and their impacts."""
    
    __tablename__ = "charter_violations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
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
