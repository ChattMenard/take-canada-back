"""Transparency campaign API - tracking government accountability across four tracks."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    EmergencyPower, SurveillanceInfrastructure, FinancialTransparency,
    CivilLibertiesLitigation, CharterViolation
)
from ..schemas import (
    EmergencyPowerCreate, EmergencyPowerRead, SurveillanceInfrastructureCreate,
    SurveillanceInfrastructureRead, FinancialTransparencyCreate,
    FinancialTransparencyRead, CivilLibertiesLitigationCreate,
    CivilLibertiesLitigationRead, CharterViolationCreate, CharterViolationRead
)

router = APIRouter(prefix="/api/transparency", tags=["transparency"])


# Emergency Powers Track
@router.post("/emergency-powers", response_model=EmergencyPowerRead)
def create_emergency_power(
    power: EmergencyPowerCreate,
    session: Session = Depends(get_session),
):
    """Document emergency powers usage and Charter rights suspensions."""
    db_power = EmergencyPower.model_validate(power)
    session.add(db_power)
    session.commit()
    session.refresh(db_power)
    return db_power


@router.get("/emergency-powers", response_model=List[EmergencyPowerRead])
def list_emergency_powers(
    power_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Get emergency powers with filtering."""
    query = select(EmergencyPower)
    
    if power_type:
        query = query.where(EmergencyPower.power_type == power_type)
    if start_date:
        query = query.where(EmergencyPower.date >= start_date)
    if end_date:
        query = query.where(EmergencyPower.date <= end_date)
    
    query = query.order_by(EmergencyPower.date.desc())
    return session.exec(query).all()


@router.get("/emergency-powers/charter-violations")
def get_charter_violations_by_emergency_powers(
    session: Session = Depends(get_session),
):
    """Analyze Charter rights violations caused by emergency powers."""
    
    emergency_powers = session.exec(
        select(EmergencyPower)
        .order_by(EmergencyPower.date.desc())
    ).all()
    
    charter_violations = session.exec(
        select(CharterViolation)
        .order_by(CharterViolation.date.desc())
    ).all()
    
    # Map violations to emergency powers
    analysis = []
    for power in emergency_powers:
        related_violations = [
            v for v in charter_violations 
            if v.violating_policy == power.title or power.title in v.violating_policy
        ]
        
        analysis.append({
            "emergency_power": power,
            "charter_violations": related_violations,
            "rights_affected": list(set([v.right_violated for v in related_violations])),
            "violation_count": len(related_violations)
        })
    
    return {
        "emergency_powers_analysis": analysis,
        "total_emergency_powers": len(emergency_powers),
        "total_charter_violations": len(charter_violations),
        "most_affected_rights": [
            right for right, count in 
            sorted(
                [(v.right_violated, len([v for v in charter_violations if v.right_violated == right])) 
                 for v in charter_violations],
                key=lambda x: x[1], reverse=True
            )
        ][:5]
    }


# Surveillance Infrastructure Track
@router.post("/surveillance", response_model=SurveillanceInfrastructureRead)
def create_surveillance_infrastructure(
    surveillance: SurveillanceInfrastructureCreate,
    session: Session = Depends(get_session),
):
    """Document surveillance infrastructure and data collection programs."""
    db_surveillance = SurveillanceInfrastructure.model_validate(surveillance)
    session.add(db_surveillance)
    session.commit()
    session.refresh(db_surveillance)
    return db_surveillance


@router.get("/surveillance", response_model=List[SurveillanceInfrastructureRead])
def list_surveillance_infrastructure(
    agency: Optional[str] = None,
    data_type: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get surveillance infrastructure with filtering."""
    query = select(SurveillanceInfrastructure)
    
    if agency:
        query = query.where(SurveillanceInfrastructure.agency == agency)
    if data_type:
        query = query.where(SurveillanceInfrastructure.data_type == data_type)
    
    query = query.order_by(SurveillanceInfrastructure.date.desc())
    return session.exec(query).all()


@router.get("/surveillance/budget-analysis")
def get_surveillance_budget_analysis(
    session: Session = Depends(get_session),
):
    """Analyze surveillance program budgets and growth."""
    
    surveillance_programs = session.exec(
        select(SurveillanceInfrastructure)
        .where(SurveillanceInfrastructure.budget_allocated.is_not(None))
        .order_by(SurveillanceInfrastructure.date.desc())
    ).all()
    
    # Group by agency
    agency_budgets = {}
    for program in surveillance_programs:
        if program.agency not in agency_budgets:
            agency_budgets[program.agency] = []
        agency_budgets[program.agency].append(program.budget_allocated)
    
    # Calculate totals and trends
    analysis = {}
    for agency, budgets in agency_budgets.items():
        analysis[agency] = {
            "total_budget": sum(budgets),
            "program_count": len(budgets),
            "average_budget": sum(budgets) / len(budgets),
            "latest_budget": budgets[0] if budgets else 0
        }
    
    return {
        "agency_analysis": analysis,
        "total_surveillance_budget": sum(p.budget_allocated for p in surveillance_programs),
        "total_programs": len(surveillance_programs),
        "data_types_collected": list(set(p.data_type for p in surveillance_programs))
    }


# Financial Transparency Track
@router.post("/financial-transparency", response_model=FinancialTransparencyRead)
def create_financial_transparency(
    financial: FinancialTransparencyCreate,
    session: Session = Depends(get_session),
):
    """Document financial system operations and transparency issues."""
    db_financial = FinancialTransparency.model_validate(financial)
    session.add(db_financial)
    session.commit()
    session.refresh(db_financial)
    return db_financial


@router.get("/financial-transparency", response_model=List[FinancialTransparencyRead])
def list_financial_transparency(
    institution: Optional[str] = None,
    operation_type: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get financial transparency records with filtering."""
    query = select(FinancialTransparency)
    
    if institution:
        query = query.where(FinancialTransparency.institution == institution)
    if operation_type:
        query = query.where(FinancialTransparency.operation_type == operation_type)
    
    query = query.order_by(FinancialTransparency.date.desc())
    return session.exec(query).all()


@router.get("/financial-transparency/bank-of-canada-analysis")
def get_bank_of_canada_analysis(
    session: Session = Depends(get_session),
):
    """Analyze Bank of Canada operations and transparency."""
    
    boc_operations = session.exec(
        select(FinancialTransparency)
        .where(FinancialTransparency.institution == "Bank of Canada")
        .order_by(FinancialTransparency.date.desc())
    ).all()
    
    # Group by operation type
    operation_analysis = {}
    for op in boc_operations:
        if op.operation_type not in operation_analysis:
            operation_analysis[op.operation_type] = []
        operation_analysis[op.operation_type].append(op)
    
    return {
        "total_operations": len(boc_operations),
        "operation_types": list(operation_analysis.keys()),
        "transparency_assessment": {
            "high_transparency": len([op for op in boc_operations if op.transparency_level == "high"]),
            "medium_transparency": len([op for op in boc_operations if op.transparency_level == "medium"]),
            "low_transparency": len([op for op in boc_operations if op.transparency_level == "low"]),
            "no_transparency": len([op for op in boc_operations if op.transparency_level == "none"])
        },
        "total_amount": sum(op.amount for op in boc_operations if op.amount),
        "operations_by_type": {
            op_type: len(ops) for op_type, ops in operation_analysis.items()
        }
    }


# Civil Liberties Litigation Track
@router.post("/civil-liberties-litigation", response_model=CivilLibertiesLitigationRead)
def create_civil_liberties_litigation(
    litigation: CivilLibertiesLitigationCreate,
    session: Session = Depends(get_session),
):
    """Document civil liberties challenges to government overreach."""
    db_litigation = CivilLibertiesLitigation.model_validate(litigation)
    session.add(db_litigation)
    session.commit()
    session.refresh(db_litigation)
    return db_litigation


@router.get("/civil-liberties-litigation", response_model=List[CivilLibertiesLitigationRead])
def list_civil_liberties_litigation(
    organization: Optional[str] = None,
    outcome: Optional[str] = None,
    court_level: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get civil liberties litigation with filtering."""
    query = select(CivilLibertiesLitigation)
    
    if organization:
        query = query.where(CivilLibertiesLitigation.organization == organization)
    if outcome:
        query = query.where(CivilLibertiesLitigation.outcome == outcome)
    if court_level:
        query = query.where(CivilLibertiesLitigation.court_level == court_level)
    
    query = query.order_by(CivilLibertiesLitigation.date.desc())
    return session.exec(query).all()


@router.get("/civil-liberties-litigation/success-rate")
def get_litigation_success_rate(
    session: Session = Depends(get_session),
):
    """Analyze success rates of civil liberties litigation."""
    
    litigation_cases = session.exec(
        select(CivilLibertiesLitigation)
    ).all()
    
    # Group by organization and outcome
    organization_stats = {}
    for case in litigation_cases:
        if case.organization not in organization_stats:
            organization_stats[case.organization] = {"total": 0, "victories": 0, "defeats": 0, "ongoing": 0}
        
        organization_stats[case.organization]["total"] += 1
        if case.outcome == "victory":
            organization_stats[case.organization]["victories"] += 1
        elif case.outcome == "defeat":
            organization_stats[case.organization]["defeats"] += 1
        elif case.outcome == "ongoing":
            organization_stats[case.organization]["ongoing"] += 1
    
    # Calculate success rates
    for org, stats in organization_stats.items():
        resolved_cases = stats["victories"] + stats["defeats"]
        stats["success_rate"] = (stats["victories"] / resolved_cases * 100) if resolved_cases > 0 else 0
    
    return {
        "organization_statistics": organization_stats,
        "overall_statistics": {
            "total_cases": len(litigation_cases),
            "total_victories": len([c for c in litigation_cases if c.outcome == "victory"]),
            "total_defeats": len([c for c in litigation_cases if c.outcome == "defeat"]),
            "ongoing_cases": len([c for c in litigation_cases if c.outcome == "ongoing"]),
            "overall_success_rate": (
                len([c for c in litigation_cases if c.outcome == "victory"]) / 
                len([c for c in litigation_cases if c.outcome in ["victory", "defeat"]]) * 100
            ) if len([c for c in litigation_cases if c.outcome in ["victory", "defeat"]]) > 0 else 0
        }
    }


# Charter Violations
@router.post("/charter-violations", response_model=CharterViolationRead)
def create_charter_violation(
    violation: CharterViolationCreate,
    session: Session = Depends(get_session),
):
    """Document specific Charter rights violations."""
    db_violation = CharterViolation.model_validate(violation)
    session.add(db_violation)
    session.commit()
    session.refresh(db_violation)
    return db_violation


@router.get("/charter-violations", response_model=List[CharterViolationRead])
def list_charter_violations(
    charter_section: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get Charter violations with filtering."""
    query = select(CharterViolation)
    
    if charter_section:
        query = query.where(CharterViolation.charter_section == charter_section)
    
    query = query.order_by(CharterViolation.date.desc())
    return session.exec(query).all()


@router.get("/charter-violations/by-section")
def get_charter_violations_by_section(
    session: Session = Depends(get_session),
):
    """Analyze Charter violations by section."""
    
    violations = session.exec(select(CharterViolation)).all()
    
    # Group by Charter section
    section_analysis = {}
    for violation in violations:
        if violation.charter_section not in section_analysis:
            section_analysis[violation.charter_section] = []
        section_analysis[violation.charter_section].append(violation)
    
    return {
        "section_analysis": {
            section: {
                "violation_count": len(violations),
                "most_common_right": max(set([v.right_violated for v in violations]), key=list([v.right_violated for v in violations]).count) if violations else None,
                "ongoing_violations": len([v for v in violations if v.ongoing_impact]),
                "court_challenges": len([v for v in violations if v.court_challenges != "none"])
            }
            for section, violations in section_analysis.items()
        },
        "total_violations": len(violations),
        "most_violated_sections": sorted(
            [(section, len(violations)) for section, violations in section_analysis.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
    }


# Overall Campaign Analysis
@router.get("/campaign-overview")
def get_transparency_campaign_overview(
    session: Session = Depends(get_session),
):
    """Get overview of all four transparency campaign tracks."""
    
    emergency_powers = session.exec(select(EmergencyPower)).all()
    surveillance = session.exec(select(SurveillanceInfrastructure)).all()
    financial = session.exec(select(FinancialTransparency)).all()
    litigation = session.exec(select(CivilLibertiesLitigation)).all()
    charter_violations = session.exec(select(CharterViolation)).all()
    
    return {
        "campaign_tracks": {
            "emergency_powers": {
                "total_records": len(emergency_powers),
                "rights_affected": len(set([p.rights_suspended for p in emergency_powers])),
                "no_oversight": len([p for p in emergency_powers if p.oversight == "none"]),
                "ongoing": len([p for p in emergency_powers if "ongoing" in p.duration.lower()])
            },
            "surveillance_infrastructure": {
                "total_records": len(surveillance),
                "agencies_involved": len(set([s.agency for s in surveillance])),
                "total_budget": sum([s.budget_allocated for s in surveillance if s.budget_allocated]),
                "data_types": len(set([s.data_type for s in surveillance])),
                "no_oversight": len([s for s in surveillance if s.oversight_mechanism == "none"])
            },
            "financial_transparency": {
                "total_records": len(financial),
                "institutions": len(set([f.institution for f in financial])),
                "total_amount": sum([f.amount for f in financial if f.amount]),
                "low_transparency": len([f for f in financial if f.transparency_level in ["low", "none"]])
            },
            "civil_liberties_litigation": {
                "total_records": len(litigation),
                "organizations": len(set([l.organization for l in litigation])),
                "victory_rate": (
                    len([l for l in litigation if l.outcome == "victory"]) / 
                    len([l for l in litigation if l.outcome in ["victory", "defeat"]]) * 100
                ) if len([l for l in litigation if l.outcome in ["victory", "defeat"]]) > 0 else 0
            },
            "charter_violations": {
                "total_records": len(charter_violations),
                "sections_violated": len(set([c.charter_section for c in charter_violations])),
                "ongoing_impacts": len([c for c in charter_violations if c.ongoing_impact]),
                "no_remedy": len([c for c in charter_violations if c.remedy_granted == "none"])
            }
        },
        "overall_assessment": {
            "total_evidence_items": len(emergency_powers) + len(surveillance) + len(financial) + len(litigation) + len(charter_violations),
            "accountability_concerns": "high",
            "transparency_level": "low",
            "citizen_risk_level": "elevated"
        }
    }
