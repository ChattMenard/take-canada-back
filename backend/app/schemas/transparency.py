"""Transparency campaign schemas for API request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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
    source_url: Optional[str] = None
    source_document: Optional[str] = None


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
    budget_allocated: Optional[float] = None
    effectiveness_claims: str
    privacy_impact: str
    source_url: Optional[str] = None


class SurveillanceInfrastructureCreate(SurveillanceInfrastructureBase):
    pass


class SurveillanceInfrastructureRead(SurveillanceInfrastructureBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class FinancialTransparencyBase(BaseModel):
    date: datetime
    institution: str
    operation_type: str
    amount: Optional[float] = None
    description: str
    stated_purpose: str
    actual_impact: str
    beneficiaries: str
    affected_groups: str
    transparency_level: str = "low"
    oversight: str = "limited"
    source_url: Optional[str] = None


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
    source_url: Optional[str] = None


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
