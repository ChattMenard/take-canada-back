"""Economic evidence collection API for tracking wealth transfer and small business destruction."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import (
    BusinessMetrics, EconomicIndicator, HypocrisyTracker, 
    PolicyAction, WealthTransfer
)
from ..schemas import (
    BusinessMetricsCreate, BusinessMetricsRead, EconomicIndicatorCreate,
    EconomicIndicatorRead, HypocrisyTrackerCreate, HypocrisyTrackerRead,
    PolicyActionCreate, PolicyActionRead, WealthTransferCreate,
    WealthTransferRead
)

router = APIRouter(prefix="/api/economic", tags=["economic"])


@router.post("/indicators", response_model=EconomicIndicatorRead)
def create_economic_indicator(
    indicator: EconomicIndicatorCreate,
    session: Session = Depends(get_session),
):
    """Add a new economic indicator data point."""
    db_indicator = EconomicIndicator.model_validate(indicator)
    session.add(db_indicator)
    session.commit()
    session.refresh(db_indicator)
    return db_indicator


@router.get("/indicators", response_model=List[EconomicIndicatorRead])
def list_economic_indicators(
    indicator_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Get economic indicators with optional filtering."""
    query = select(EconomicIndicator)
    
    if indicator_type:
        query = query.where(EconomicIndicator.indicator_type == indicator_type)
    if start_date:
        query = query.where(EconomicIndicator.date >= start_date)
    if end_date:
        query = query.where(EconomicIndicator.date <= end_date)
    
    query = query.order_by(EconomicIndicator.date.desc())
    return session.exec(query).all()


@router.post("/business-metrics", response_model=BusinessMetricsRead)
def create_business_metrics(
    metrics: BusinessMetricsCreate,
    session: Session = Depends(get_session),
):
    """Add business performance metrics."""
    db_metrics = BusinessMetrics.model_validate(metrics)
    session.add(db_metrics)
    session.commit()
    session.refresh(db_metrics)
    return db_metrics


@router.get("/business-metrics", response_model=List[BusinessMetricsRead])
def list_business_metrics(
    business_size: Optional[str] = None,
    sector: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Get business metrics with filtering."""
    query = select(BusinessMetrics)
    
    if business_size:
        query = query.where(BusinessMetrics.business_size == business_size)
    if sector:
        query = query.where(BusinessMetrics.sector == sector)
    if start_date:
        query = query.where(BusinessMetrics.date >= start_date)
    if end_date:
        query = query.where(BusinessMetrics.date <= end_date)
    
    query = query.order_by(BusinessMetrics.date.desc())
    return session.exec(query).all()


@router.post("/policy-actions", response_model=PolicyActionRead)
def create_policy_action(
    policy: PolicyActionCreate,
    session: Session = Depends(get_session),
):
    """Document a government policy action and its impacts."""
    db_policy = PolicyAction.model_validate(policy)
    session.add(db_policy)
    session.commit()
    session.refresh(db_policy)
    return db_policy


@router.get("/policy-actions", response_model=List[PolicyActionRead])
def list_policy_actions(
    policy_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Get policy actions with filtering."""
    query = select(PolicyAction)
    
    if policy_type:
        query = query.where(PolicyAction.policy_type == policy_type)
    if start_date:
        query = query.where(PolicyAction.date >= start_date)
    if end_date:
        query = query.where(PolicyAction.date <= end_date)
    
    query = query.order_by(PolicyAction.date.desc())
    return session.exec(query).all()


@router.post("/hypocrisy", response_model=HypocrisyTrackerRead)
def create_hypocrisy_entry(
    hypocrisy: HypocrisyTrackerCreate,
    session: Session = Depends(get_session),
):
    """Document government hypocrisy - statements vs. harmful actions."""
    db_hypocrisy = HypocrisyTracker.model_validate(hypocrisy)
    session.add(db_hypocrisy)
    session.commit()
    session.refresh(db_hypocrisy)
    return db_hypocrisy


@router.get("/hypocrisy", response_model=List[HypocrisyTrackerRead])
def list_hypocrisy_entries(
    official: Optional[str] = None,
    verified: Optional[bool] = None,
    session: Session = Depends(get_session),
):
    """Get hypocrisy tracker entries."""
    query = select(HypocrisyTracker)
    
    if official:
        query = query.where(HypocrisyTracker.official == official)
    if verified is not None:
        query = query.where(HypocrisyTracker.verified == verified)
    
    query = query.order_by(HypocrisyTracker.date.desc())
    return session.exec(query).all()


@router.post("/wealth-transfer", response_model=WealthTransferRead)
def create_wealth_transfer(
    transfer: WealthTransferCreate,
    session: Session = Depends(get_session),
):
    """Document a specific wealth transfer mechanism."""
    db_transfer = WealthTransfer.model_validate(transfer)
    session.add(db_transfer)
    session.commit()
    session.refresh(db_transfer)
    return db_transfer


@router.get("/wealth-transfer", response_model=List[WealthTransferRead])
def list_wealth_transfers(
    mechanism: Optional[str] = None,
    from_group: Optional[str] = None,
    to_group: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """Get wealth transfer records."""
    query = select(WealthTransfer)
    
    if mechanism:
        query = query.where(WealthTransfer.mechanism == mechanism)
    if from_group:
        query = query.where(WealthTransfer.from_group == from_group)
    if to_group:
        query = query.where(WealthTransfer.to_group == to_group)
    
    query = query.order_by(WealthTransfer.date.desc())
    return session.exec(query).all()


@router.get("/small-business-destruction")
def get_small_business_destruction_analysis(
    session: Session = Depends(get_session),
):
    """Analyze small business destruction patterns."""
    # Get small business metrics over time
    small_business_metrics = session.exec(
        select(BusinessMetrics)
        .where(BusinessMetrics.business_size == "small")
        .order_by(BusinessMetrics.date.desc())
        .limit(100)
    ).all()
    
    # Get inflation policies
    inflation_policies = session.exec(
        select(PolicyAction)
        .where(PolicyAction.policy_type == "inflation")
        .order_by(PolicyAction.date.desc())
        .limit(50)
    ).all()
    
    return {
        "business_metrics": small_business_metrics,
        "related_policies": inflation_policies,
        "analysis": {
            "trend": "declining_profits_with_rising_costs",
            "mechanism": "inflation_tax_on_small_business",
            "evidence_count": len(small_business_metrics) + len(inflation_policies)
        }
    }


@router.get("/inflation-tax-tracker")
def get_inflation_tax_analysis(
    session: Session = Depends(get_session),
):
    """Track how inflation acts as a tax on citizens while benefiting elites."""
    
    # Get inflation indicators
    inflation_data = session.exec(
        select(EconomicIndicator)
        .where(EconomicIndicator.indicator_type == "inflation_rate")
        .order_by(EconomicIndicator.date.desc())
        .limit(50)
    ).all()
    
    # Get wealth transfers tagged as inflation_tax
    inflation_transfers = session.exec(
        select(WealthTransfer)
        .where(WealthTransfer.mechanism == "inflation_tax")
        .order_by(WealthTransfer.date.desc())
        .limit(50)
    ).all()
    
    # Get hypocrisy entries about inflation
    inflation_hypocrisy = session.exec(
        select(HypocrisyTracker)
        .where(HypocrisyTracker.contradictory_action.like("%inflation%"))
        .order_by(HypocrisyTracker.date.desc())
        .limit(20)
    ).all()
    
    return {
        "inflation_rates": inflation_data,
        "wealth_transfers": inflation_transfers,
        "government_hypocrisy": inflation_hypocrisy,
        "total_transferred": sum(t.amount for t in inflation_transfers),
        "mechanism_summary": "Inflation reduces purchasing power of wages/savings while benefiting asset holders and government through increased tax revenue"
    }
