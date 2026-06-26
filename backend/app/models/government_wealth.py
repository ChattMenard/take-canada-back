"""
Government Wealth Tracking Models
Veritas Evidence Collection System
"""

from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import List, Optional

Base = declarative_base()

# SQLAlchemy Models
class OfficialAssetDeclaration(Base):
    __tablename__ = 'official_asset_declarations'
    
    id = Column(Integer, primary_key=True)
    official_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    declaration_date = Column(Date, nullable=False)
    file_path = Column(Text)  # Path to stored document
    
    # Relationships
    assets = relationship("AssetHolding", back_populates="declaration")
    spouse_assets = relationship("SpouseAssetHolding", back_populates="declaration")
    business_interests = relationship("BusinessInterest", back_populates="declaration")
    conflicts = relationship("ConflictAssessment", back_populates="declaration")

class AssetHolding(Base):
    __tablename__ = 'asset_holdings'
    
    id = Column(Integer, primary_key=True)
    declaration_id = Column(Integer, ForeignKey('official_asset_declarations.id'))
    asset_type = Column(String(100))  # stock, bond, real estate, business
    description = Column(Text)
    value_range = Column(String(50))  # "$100,001-$250,000"
    acquisition_date = Column(Date)
    disposition_date = Column(Date, nullable=True)
    policy_sensitive = Column(Boolean, default=False)
    
    # Relationships
    declaration = relationship("OfficialAssetDeclaration", back_populates="assets")

class SpouseAssetHolding(Base):
    __tablename__ = 'spouse_asset_holdings'
    
    id = Column(Integer, primary_key=True)
    declaration_id = Column(Integer, ForeignKey('official_asset_declarations.id'))
    asset_type = Column(String(100))
    description = Column(Text)
    value_range = Column(String(50))
    acquisition_date = Column(Date)
    disposition_date = Column(Date, nullable=True)
    policy_sensitive = Column(Boolean, default=False)
    
    # Relationships
    declaration = relationship("OfficialAssetDeclaration", back_populates="spouse_assets")

class BusinessInterest(Base):
    __tablename__ = 'business_interests'
    
    id = Column(Integer, primary_key=True)
    declaration_id = Column(Integer, ForeignKey('official_asset_declarations.id'))
    company_name = Column(String(255))
    ownership_percentage = Column(Numeric(5, 2))
    role = Column(String(100))  # owner, director, officer, advisor
    sector = Column(String(100))
    policy_sensitive = Column(Boolean, default=False)
    revenue = Column(Numeric(15, 2), nullable=True)
    establishment_date = Column(Date)
    recent_growth = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    declaration = relationship("OfficialAssetDeclaration", back_populates="business_interests")

class PolicyDecision(Base):
    __tablename__ = 'policy_decisions'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(String(100), unique=True, nullable=False)
    policy_title = Column(Text, nullable=False)
    decision_type = Column(String(100))  # regulatory, spending, tax, procurement
    proposal_date = Column(Date)
    announcement_date = Column(Date)
    implementation_date = Column(Date)
    affected_sectors = Column(Text)  # JSON string of sectors
    decision_makers = Column(Text)  # JSON string of officials
    supporting_documents = Column(Text)  # JSON string of document paths
    
    # Relationships
    correlations = relationship("PolicyTransactionCorrelation", back_populates="policy")
    impacts = relationship("PolicyCorporateImpact", back_populates="policy")

class FinancialTransaction(Base):
    __tablename__ = 'financial_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True)
    person_name = Column(String(255))
    relationship_to_official = Column(String(100))
    transaction_type = Column(String(50))  # buy, sell, establish, appoint
    asset_description = Column(Text)
    transaction_date = Column(Date)
    transaction_value = Column(Numeric(15, 2))
    asset_sector = Column(String(100))
    policy_sensitive = Column(Boolean, default=False)
    
    # Relationships
    correlations = relationship("PolicyTransactionCorrelation", back_populates="transaction")

class PolicyTransactionCorrelation(Base):
    __tablename__ = 'policy_transaction_correlations'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy_decisions.id'))
    transaction_id = Column(Integer, ForeignKey('financial_transactions.id'))
    time_advantage_days = Column(Integer)
    value_impact_percent = Column(Numeric(5, 2))
    sector_match = Column(Boolean, default=False)
    decision_maker_involved = Column(Boolean, default=False)
    correlation_score = Column(Numeric(3, 2))  # 0-1 probability
    confidence_level = Column(String(20))  # high, medium, low
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("PolicyDecision", back_populates="correlations")
    transaction = relationship("FinancialTransaction", back_populates="correlations")

class GovernmentContract(Base):
    __tablename__ = 'government_contracts'
    
    id = Column(Integer, primary_key=True)
    contract_number = Column(String(100), unique=True)
    department = Column(String(255))
    contractor_name = Column(String(255))
    contract_value = Column(Numeric(15, 2))
    award_date = Column(Date)
    procurement_method = Column(String(100))  # competitive, sole-source, emergency
    official_involvement = Column(String(255))
    
    # Relationships
    ownership_entities = relationship("OwnershipEntity", back_populates="contract")
    amendments = relationship("ContractAmendment", back_populates="contract")

class OwnershipEntity(Base):
    __tablename__ = 'ownership_entities'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('government_contracts.id'))
    entity_name = Column(String(255))
    ownership_percentage = Column(Numeric(5, 2))
    
    # Relationships
    contract = relationship("GovernmentContract", back_populates="ownership_entities")

class ContractAmendment(Base):
    __tablename__ = 'contract_amendments'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('government_contracts.id'))
    amendment_date = Column(Date)
    original_value = Column(Numeric(15, 2))
    amended_value = Column(Numeric(15, 2))
    justification = Column(Text)
    
    # Relationships
    contract = relationship("GovernmentContract", back_populates="amendments")

class ConflictAssessment(Base):
    __tablename__ = 'conflict_assessments'
    
    id = Column(Integer, primary_key=True)
    declaration_id = Column(Integer, ForeignKey('official_asset_declarations.id'))
    assessment_date = Column(Date)
    policy_matter = Column(Text)
    conflict_found = Column(Boolean, default=False)
    resolution = Column(Text)
    
    # Relationships
    declaration = relationship("OfficialAssetDeclaration", back_populates="conflicts")

class FamilyBusinessNetwork(Base):
    __tablename__ = 'family_business_networks'
    
    id = Column(Integer, primary_key=True)
    central_official = Column(String(255))
    network_type = Column(String(100))  # immediate, extended, associates
    relationship_count = Column(Integer)
    business_count = Column(Integer)
    total_estimated_value = Column(Numeric(15, 2))
    last_updated = Column(DateTime, default=datetime.utcnow)

class PolicyCorporateImpact(Base):
    __tablename__ = 'policy_corporate_impacts'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy_decisions.id'))
    corporation = Column(String(255))
    impact_type = Column(String(100))  # land_value, development_cost, market_access
    pre_policy_value = Column(Numeric(15, 2))
    post_policy_value = Column(Numeric(15, 2))
    impact_duration_months = Column(Integer)
    confidence_level = Column(String(20))
    
    # Relationships
    policy = relationship("PolicyDecision", back_populates="impacts")


# Pydantic Models for API
class AssetHoldingCreate(BaseModel):
    asset_type: str
    description: str
    value_range: str
    acquisition_date: date
    disposition_date: Optional[date] = None
    policy_sensitive: bool = False

class BusinessInterestCreate(BaseModel):
    company_name: str
    ownership_percentage: float = Field(ge=0, le=100)
    role: str
    sector: str
    policy_sensitive: bool = False
    revenue: Optional[float] = None
    establishment_date: date
    recent_growth: Optional[float] = None

class PolicyDecisionCreate(BaseModel):
    policy_id: str
    policy_title: str
    decision_type: str
    proposal_date: date
    announcement_date: date
    implementation_date: date
    affected_sectors: List[str]
    decision_makers: List[str]

class PolicyTransactionCorrelationCreate(BaseModel):
    policy_id: int
    transaction_id: int
    time_advantage_days: int
    value_impact_percent: Optional[float] = None
    sector_match: bool = False
    decision_maker_involved: bool = False
    correlation_score: float = Field(ge=0, le=1)
    confidence_level: str  # high, medium, low

class GovernmentContractCreate(BaseModel):
    contract_number: str
    department: str
    contractor_name: str
    contract_value: float
    award_date: date
    procurement_method: str
    official_involvement: str

class OwnershipEntityCreate(BaseModel):
    entity_name: str
    ownership_percentage: float = Field(ge=0, le=100)

class ContractAmendmentCreate(BaseModel):
    amendment_date: date
    original_value: float
    amended_value: float
    justification: str


# Analysis Functions
def calculate_correlation_score(time_advantage_days: int, value_impact_percent: float, 
                             sector_match: bool, decision_maker_involved: bool) -> float:
    """
    Calculate correlation score for policy-transaction relationships.
    Returns value between 0 and 1.
    """
    score = 0.0
    
    # Time advantage scoring (0-0.4)
    if time_advantage_days > 0:
        if time_advantage_days <= 30:
            score += 0.4
        elif time_advantage_days <= 60:
            score += 0.3
        elif time_advantage_days <= 90:
            score += 0.2
        elif time_advantage_days <= 180:
            score += 0.1
    
    # Value impact scoring (0-0.3)
    if value_impact_percent and value_impact_percent > 0:
        if value_impact_percent >= 50:
            score += 0.3
        elif value_impact_percent >= 25:
            score += 0.2
        elif value_impact_percent >= 10:
            score += 0.1
    
    # Sector match scoring (0-0.2)
    if sector_match:
        score += 0.2
    
    # Decision maker involvement scoring (0-0.1)
    if decision_maker_involved:
        score += 0.1
    
    return min(score, 1.0)

def determine_confidence_level(correlation_score: float, data_quality: str) -> str:
    """
    Determine confidence level based on correlation score and data quality.
    """
    if correlation_score >= 0.8 and data_quality == "high":
        return "high"
    elif correlation_score >= 0.6 and data_quality in ["high", "medium"]:
        return "medium"
    else:
        return "low"

def detect_timing_pattern(official_name: str, policy_date: date, 
                         transaction_date: date) -> dict:
    """
    Detect if transaction shows timing advantage pattern.
    """
    days_difference = (policy_date - transaction_date).days
    
    if 30 <= days_difference <= 180:
        return {
            "pattern_detected": True,
            "pattern_type": "pre_policy_acquisition",
            "time_advantage_days": days_difference,
            "significance": "high" if days_difference <= 60 else "medium"
        }
    elif -180 <= days_difference <= -30:
        return {
            "pattern_detected": True,
            "pattern_type": "pre_policy_disposition",
            "time_advantage_days": abs(days_difference),
            "significance": "high" if abs(days_difference) <= 60 else "medium"
        }
    else:
        return {
            "pattern_detected": False,
            "pattern_type": None,
            "time_advantage_days": 0,
            "significance": None
        }
