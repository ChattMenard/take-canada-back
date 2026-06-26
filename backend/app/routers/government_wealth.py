"""
Government Wealth Tracking API Endpoints
Veritas Evidence Collection System
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import json

from ..database import get_db
from ..models.government_wealth import (
    OfficialAssetDeclaration, AssetHolding, BusinessInterest, 
    PolicyDecision, FinancialTransaction, PolicyTransactionCorrelation,
    GovernmentContract, OwnershipEntity, ContractAmendment,
    AssetHoldingCreate, BusinessInterestCreate, PolicyDecisionCreate,
    PolicyTransactionCorrelationCreate, GovernmentContractCreate,
    OwnershipEntityCreate, ContractAmendmentCreate,
    calculate_correlation_score, determine_confidence_level, detect_timing_pattern
)

router = APIRouter(prefix="/government-wealth", tags=["government-wealth"])

# Asset Declaration Endpoints
@router.post("/declarations/", response_model=dict)
async def create_asset_declaration(
    official_name: str,
    position: str,
    declaration_date: date,
    db: Session = Depends(get_db)
):
    """Create a new official asset declaration."""
    declaration = OfficialAssetDeclaration(
        official_name=official_name,
        position=position,
        declaration_date=declaration_date
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    
    return {
        "id": declaration.id,
        "official_name": declaration.official_name,
        "position": declaration.position,
        "declaration_date": declaration.declaration_date,
        "created_at": datetime.utcnow()
    }

@router.get("/declarations/", response_model=List[dict])
async def get_asset_declarations(
    official_name: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get asset declarations with optional filtering."""
    query = db.query(OfficialAssetDeclaration)
    
    if official_name:
        query = query.filter(OfficialAssetDeclaration.official_name.ilike(f"%{official_name}%"))
    if position:
        query = query.filter(OfficialAssetDeclaration.position.ilike(f"%{position}%"))
    
    declarations = query.all()
    
    results = []
    for decl in declarations:
        results.append({
            "id": decl.id,
            "official_name": decl.official_name,
            "position": decl.position,
            "declaration_date": decl.declaration_date,
            "asset_count": len(decl.assets),
            "business_interest_count": len(decl.business_interests),
            "conflict_count": len(decl.conflicts)
        })
    
    return results

@router.post("/declarations/{declaration_id}/assets/", response_model=dict)
async def add_asset_holding(
    declaration_id: int,
    asset: AssetHoldingCreate,
    db: Session = Depends(get_db)
):
    """Add an asset holding to a declaration."""
    declaration = db.query(OfficialAssetDeclaration).filter(
        OfficialAssetDeclaration.id == declaration_id
    ).first()
    
    if not declaration:
        raise HTTPException(status_code=404, detail="Declaration not found")
    
    asset_holding = AssetHolding(
        declaration_id=declaration_id,
        **asset.dict()
    )
    db.add(asset_holding)
    db.commit()
    db.refresh(asset_holding)
    
    return {
        "id": asset_holding.id,
        "declaration_id": asset_holding.declaration_id,
        "asset_type": asset_holding.asset_type,
        "description": asset_holding.description,
        "value_range": asset_holding.value_range,
        "acquisition_date": asset_holding.acquisition_date,
        "policy_sensitive": asset_holding.policy_sensitive
    }

@router.post("/declarations/{declaration_id}/business-interests/", response_model=dict)
async def add_business_interest(
    declaration_id: int,
    business: BusinessInterestCreate,
    db: Session = Depends(get_db)
):
    """Add a business interest to a declaration."""
    declaration = db.query(OfficialAssetDeclaration).filter(
        OfficialAssetDeclaration.id == declaration_id
    ).first()
    
    if not declaration:
        raise HTTPException(status_code=404, detail="Declaration not found")
    
    business_interest = BusinessInterest(
        declaration_id=declaration_id,
        **business.dict()
    )
    db.add(business_interest)
    db.commit()
    db.refresh(business_interest)
    
    return {
        "id": business_interest.id,
        "declaration_id": business_interest.declaration_id,
        "company_name": business_interest.company_name,
        "ownership_percentage": float(business_interest.ownership_percentage),
        "role": business_interest.role,
        "sector": business_interest.sector,
        "policy_sensitive": business_interest.policy_sensitive
    }

# Policy Decision Endpoints
@router.post("/policy-decisions/", response_model=dict)
async def create_policy_decision(
    policy: PolicyDecisionCreate,
    db: Session = Depends(get_db)
):
    """Create a new policy decision record."""
    policy_decision = PolicyDecision(
        policy_id=policy.policy_id,
        policy_title=policy.policy_title,
        decision_type=policy.decision_type,
        proposal_date=policy.proposal_date,
        announcement_date=policy.announcement_date,
        implementation_date=policy.implementation_date,
        affected_sectors=json.dumps(policy.affected_sectors),
        decision_makers=json.dumps(policy.decision_makers)
    )
    db.add(policy_decision)
    db.commit()
    db.refresh(policy_decision)
    
    return {
        "id": policy_decision.id,
        "policy_id": policy_decision.policy_id,
        "policy_title": policy_decision.policy_title,
        "decision_type": policy_decision.decision_type,
        "announcement_date": policy_decision.announcement_date,
        "affected_sectors": json.loads(policy_decision.affected_sectors),
        "decision_makers": json.loads(policy_decision.decision_makers)
    }

@router.get("/policy-decisions/", response_model=List[dict])
async def get_policy_decisions(
    decision_type: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get policy decisions with optional filtering."""
    query = db.query(PolicyDecision)
    
    if decision_type:
        query = query.filter(PolicyDecision.decision_type == decision_type)
    
    decisions = query.all()
    
    results = []
    for decision in decisions:
        affected_sectors = json.loads(decision.affected_sectors) if decision.affected_sectors else []
        decision_makers = json.loads(decision.decision_makers) if decision.decision_makers else []
        
        # Filter by sector if specified
        if sector and sector not in affected_sectors:
            continue
        
        results.append({
            "id": decision.id,
            "policy_id": decision.policy_id,
            "policy_title": decision.policy_title,
            "decision_type": decision.decision_type,
            "proposal_date": decision.proposal_date,
            "announcement_date": decision.announcement_date,
            "implementation_date": decision.implementation_date,
            "affected_sectors": affected_sectors,
            "decision_makers": decision_makers,
            "correlation_count": len(decision.correlations)
        })
    
    return results

# Transaction Correlation Analysis
@router.post("/correlations/", response_model=dict)
async def create_correlation(
    correlation: PolicyTransactionCorrelationCreate,
    db: Session = Depends(get_db)
):
    """Create a policy-transaction correlation analysis."""
    # Validate policy and transaction exist
    policy = db.query(PolicyDecision).filter(PolicyDecision.id == correlation.policy_id).first()
    transaction = db.query(FinancialTransaction).filter(FinancialTransaction.id == correlation.transaction_id).first()
    
    if not policy or not transaction:
        raise HTTPException(status_code=404, detail="Policy or transaction not found")
    
    # Auto-calculate correlation score if not provided
    if correlation.correlation_score == 0:
        correlation_score = calculate_correlation_score(
            correlation.time_advantage_days,
            correlation.value_impact_percent or 0,
            correlation.sector_match,
            correlation.decision_maker_involved
        )
        correlation.correlation_score = correlation_score
    
    # Auto-determine confidence level
    confidence_level = determine_confidence_level(correlation.correlation_score, "high")
    
    correlation_record = PolicyTransactionCorrelation(
        **correlation.dict(),
        confidence_level=confidence_level
    )
    db.add(correlation_record)
    db.commit()
    db.refresh(correlation_record)
    
    return {
        "id": correlation_record.id,
        "policy_id": correlation_record.policy_id,
        "transaction_id": correlation_record.transaction_id,
        "time_advantage_days": correlation_record.time_advantage_days,
        "correlation_score": float(correlation_record.correlation_score),
        "confidence_level": correlation_record.confidence_level,
        "analysis_date": correlation_record.analysis_date
    }

@router.get("/correlations/", response_model=List[dict])
async def get_correlations(
    confidence_level: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get policy-transaction correlations with filtering."""
    query = db.query(PolicyTransactionCorrelation)
    
    if confidence_level:
        query = query.filter(PolicyTransactionCorrelation.confidence_level == confidence_level)
    if min_score:
        query = query.filter(PolicyTransactionCorrelation.correlation_score >= min_score)
    
    correlations = query.all()
    
    results = []
    for corr in correlations:
        results.append({
            "id": corr.id,
            "policy_id": corr.policy_id,
            "transaction_id": corr.transaction_id,
            "time_advantage_days": corr.time_advantage_days,
            "value_impact_percent": float(corr.value_impact_percent) if corr.value_impact_percent else None,
            "sector_match": corr.sector_match,
            "decision_maker_involved": corr.decision_maker_involved,
            "correlation_score": float(corr.correlation_score),
            "confidence_level": corr.confidence_level,
            "analysis_date": corr.analysis_date
        })
    
    return results

# Government Contract Endpoints
@router.post("/contracts/", response_model=dict)
async def create_government_contract(
    contract: GovernmentContractCreate,
    db: Session = Depends(get_db)
):
    """Create a new government contract record."""
    gov_contract = GovernmentContract(**contract.dict())
    db.add(gov_contract)
    db.commit()
    db.refresh(gov_contract)
    
    return {
        "id": gov_contract.id,
        "contract_number": gov_contract.contract_number,
        "department": gov_contract.department,
        "contractor_name": gov_contract.contractor_name,
        "contract_value": float(gov_contract.contract_value),
        "award_date": gov_contract.award_date,
        "procurement_method": gov_contract.procurement_method,
        "official_involvement": gov_contract.official_involvement
    }

@router.get("/contracts/", response_model=List[dict])
async def get_government_contracts(
    department: Optional[str] = None,
    procurement_method: Optional[str] = None,
    min_value: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get government contracts with filtering."""
    query = db.query(GovernmentContract)
    
    if department:
        query = query.filter(GovernmentContract.department.ilike(f"%{department}%"))
    if procurement_method:
        query = query.filter(GovernmentContract.procurement_method == procurement_method)
    if min_value:
        query = query.filter(GovernmentContract.contract_value >= min_value)
    
    contracts = query.all()
    
    results = []
    for contract in contracts:
        results.append({
            "id": contract.id,
            "contract_number": contract.contract_number,
            "department": contract.department,
            "contractor_name": contract.contractor_name,
            "contract_value": float(contract.contract_value),
            "award_date": contract.award_date,
            "procurement_method": contract.procurement_method,
            "official_involvement": contract.official_involvement,
            "ownership_entity_count": len(contract.ownership_entities),
            "amendment_count": len(contract.amendments)
        })
    
    return results

@router.post("/contracts/{contract_id}/ownership/", response_model=dict)
async def add_ownership_entity(
    contract_id: int,
    ownership: OwnershipEntityCreate,
    db: Session = Depends(get_db)
):
    """Add ownership entity to a government contract."""
    contract = db.query(GovernmentContract).filter(GovernmentContract.id == contract_id).first()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    ownership_entity = OwnershipEntity(
        contract_id=contract_id,
        **ownership.dict()
    )
    db.add(ownership_entity)
    db.commit()
    db.refresh(ownership_entity)
    
    return {
        "id": ownership_entity.id,
        "contract_id": ownership_entity.contract_id,
        "entity_name": ownership_entity.entity_name,
        "ownership_percentage": float(ownership_entity.ownership_percentage)
    }

# Analysis Endpoints
@router.get("/analysis/timing-patterns/", response_model=List[dict])
async def analyze_timing_patterns(
    official_name: str,
    db: Session = Depends(get_db)
):
    """Analyze timing patterns for a specific official."""
    # Get official's declarations
    declarations = db.query(OfficialAssetDeclaration).filter(
        OfficialAssetDeclaration.official_name.ilike(f"%{official_name}%")
    ).all()
    
    # Get relevant policies
    policies = db.query(PolicyDecision).all()
    
    patterns = []
    
    for declaration in declarations:
        # Get assets
        for asset in declaration.assets:
            for policy in policies:
                if asset.acquisition_date and policy.announcement_date:
                    pattern = detect_timing_pattern(
                        declaration.official_name,
                        policy.announcement_date,
                        asset.acquisition_date
                    )
                    
                    if pattern["pattern_detected"]:
                        patterns.append({
                            "official_name": declaration.official_name,
                            "position": declaration.position,
                            "asset_description": asset.description,
                            "asset_type": asset.asset_type,
                            "acquisition_date": asset.acquisition_date,
                            "policy_title": policy.policy_title,
                            "policy_announcement_date": policy.announcement_date,
                            "pattern_type": pattern["pattern_type"],
                            "time_advantage_days": pattern["time_advantage_days"],
                            "significance": pattern["significance"]
                        })
    
    return patterns

@router.get("/analysis/summary/", response_model=dict)
async def get_analysis_summary(db: Session = Depends(get_db)):
    """Get overall analysis summary statistics."""
    
    # Count records
    declaration_count = db.query(OfficialAssetDeclaration).count()
    policy_count = db.query(PolicyDecision).count()
    contract_count = db.query(GovernmentContract).count()
    correlation_count = db.query(PolicyTransactionCorrelation).count()
    
    # High-confidence correlations
    high_confidence_correlations = db.query(PolicyTransactionCorrelation).filter(
        PolicyTransactionCorrelation.confidence_level == "high"
    ).count()
    
    # Sole-source contracts
    sole_source_contracts = db.query(GovernmentContract).filter(
        GovernmentContract.procurement_method == "sole-source"
    ).count()
    
    # Policy-sensitive assets
    policy_sensitive_assets = db.query(AssetHolding).filter(
        AssetHolding.policy_sensitive == True
    ).count()
    
    return {
        "total_records": {
            "asset_declarations": declaration_count,
            "policy_decisions": policy_count,
            "government_contracts": contract_count,
            "correlations": correlation_count
        },
        "key_findings": {
            "high_confidence_correlations": high_confidence_correlations,
            "sole_source_contracts": sole_source_contracts,
            "policy_sensitive_assets": policy_sensitive_assets
        },
        "analysis_metrics": {
            "correlation_rate": (correlation_count / max(policy_count, 1)) * 100,
            "sole_source_rate": (sole_source_contracts / max(contract_count, 1)) * 100,
            "policy_sensitive_rate": (policy_sensitive_assets / max(
                db.query(AssetHolding).count(), 1
            )) * 100
        },
        "last_updated": datetime.utcnow()
    }

# Evidence Upload Endpoints
@router.post("/upload/declaration/", response_model=dict)
async def upload_declaration_document(
    declaration_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a declaration document file."""
    declaration = db.query(OfficialAssetDeclaration).filter(
        OfficialAssetDeclaration.id == declaration_id
    ).first()
    
    if not declaration:
        raise HTTPException(status_code=404, detail="Declaration not found")
    
    # Save file (implement actual file storage logic)
    file_path = f"/uploads/declarations/{declaration_id}_{file.filename}"
    
    # Update declaration with file path
    declaration.file_path = file_path
    db.commit()
    
    return {
        "declaration_id": declaration_id,
        "file_name": file.filename,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow()
    }

@router.get("/health/", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "government-wealth-tracking",
        "timestamp": datetime.utcnow()
    }
