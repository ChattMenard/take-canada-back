"""Wealth gap policy impact tracker - analyzing how policies widen or narrow wealth inequality."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from ..database import get_session
from ..models import EconomicIndicator, PolicyAction, WealthTransfer, BusinessMetrics
from ..schemas import EconomicIndicatorRead, PolicyActionRead, WealthTransferRead

router = APIRouter(prefix="/api/wealth-gap", tags=["wealth-gap"])


@router.get("/policy-impact-analysis")
def analyze_policy_impact_on_wealth_gap(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Analyze how specific policies have impacted wealth distribution."""
    
    # Get policies in date range
    query = select(PolicyAction)
    if start_date:
        query = query.where(PolicyAction.date >= start_date)
    if end_date:
        query = query.where(PolicyAction.date <= end_date)
    
    policies = session.exec(query.order_by(PolicyAction.date.desc())).all()
    
    analysis = []
    for policy in policies:
        # Get related economic indicators before and after policy
        pre_indicators = session.exec(
            select(EconomicIndicator)
            .where(
                EconomicIndicator.date < policy.date,
                EconomicIndicator.indicator_type.in_(["wealth_gap", "gini_coefficient", "top_1_percent_share"])
            )
            .order_by(EconomicIndicator.date.desc())
            .limit(5)
        ).all()
        
        post_indicators = session.exec(
            select(EconomicIndicator)
            .where(
                EconomicIndicator.date >= policy.date,
                EconomicIndicator.indicator_type.in_(["wealth_gap", "gini_coefficient", "top_1_percent_share"])
            )
            .order_by(EconomicIndicator.date.asc())
            .limit(5)
        ).all()
        
        # Calculate impact
        pre_avg = sum(ind.value for ind in pre_indicators) / len(pre_indicators) if pre_indicators else 0
        post_avg = sum(ind.value for ind in post_indicators) / len(post_indicators) if post_indicators else 0
        
        impact_direction = "widened" if post_avg > pre_avg else "narrowed" if post_avg < pre_avg else "no_change"
        
        analysis.append({
            "policy": policy,
            "pre_policy_average": pre_avg,
            "post_policy_average": post_avg,
            "impact_direction": impact_direction,
            "impact_magnitude": abs(post_avg - pre_avg),
            "data_points": len(pre_indicators) + len(post_indicators)
        })
    
    return {
        "policy_impacts": analysis,
        "total_policies_analyzed": len(analysis),
        "widening_policies": len([a for a in analysis if a["impact_direction"] == "widened"]),
        "narrowing_policies": len([a for a in analysis if a["impact_direction"] == "narrowed"])
    }


@router.get("/wealth-transfer-totals")
def get_wealth_transfer_totals(
    mechanism: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Get total wealth transferred by mechanism and time period."""
    
    query = select(WealthTransfer)
    if mechanism:
        query = query.where(WealthTransfer.mechanism == mechanism)
    if start_date:
        query = query.where(WealthTransfer.date >= start_date)
    if end_date:
        query = query.where(WealthTransfer.date <= end_date)
    
    transfers = session.exec(query).all()
    
    # Group by mechanism
    mechanism_totals = {}
    for transfer in transfers:
        if transfer.mechanism not in mechanism_totals:
            mechanism_totals[transfer.mechanism] = 0
        mechanism_totals[transfer.mechanism] += transfer.amount
    
    # Group by from/to groups
    from_group_totals = {}
    to_group_totals = {}
    
    for transfer in transfers:
        if transfer.from_group not in from_group_totals:
            from_group_totals[transfer.from_group] = 0
        from_group_totals[transfer.from_group] += transfer.amount
        
        if transfer.to_group not in to_group_totals:
            to_group_totals[transfer.to_group] = 0
        to_group_totals[transfer.to_group] += transfer.amount
    
    return {
        "total_transferred": sum(t.amount for t in transfers),
        "by_mechanism": mechanism_totals,
        "from_groups": from_group_totals,
        "to_groups": to_group_totals,
        "transfer_count": len(transfers)
    }


@router.get("/small-business-vs-corporate-performance")
def compare_small_business_vs_corporate_performance(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
):
    """Compare performance metrics between small businesses and large corporations."""
    
    query = select(BusinessMetrics)
    if start_date:
        query = query.where(BusinessMetrics.date >= start_date)
    if end_date:
        query = query.where(BusinessMetrics.date <= end_date)
    
    # Get small business metrics
    small_business_metrics = session.exec(
        query.where(BusinessMetrics.business_size == "small")
        .order_by(BusinessMetrics.date.desc())
    ).all()
    
    # Get corporate metrics
    corporate_metrics = session.exec(
        query.where(BusinessMetrics.business_size.in_(["large", "corporate"]))
        .order_by(BusinessMetrics.date.desc())
    ).all()
    
    # Calculate profit margins and growth rates
    small_analysis = analyze_business_performance(small_business_metrics)
    corporate_analysis = analyze_business_performance(corporate_metrics)
    
    return {
        "small_business_performance": small_analysis,
        "corporate_performance": corporate_analysis,
        "performance_gap": {
            "profit_margin_gap": corporate_analysis["avg_profit_margin"] - small_analysis["avg_profit_margin"],
            "growth_rate_gap": corporate_analysis["avg_growth_rate"] - small_analysis["avg_growth_rate"],
            "closure_rate_diff": small_analysis["avg_closure_rate"] - corporate_analysis.get("avg_closure_rate", 0)
        }
    }


@router.get("/wealth-gap-timeline")
def get_wealth_gap_timeline(
    session: Session = Depends(get_session),
):
    """Get timeline of wealth gap changes with related policy events."""
    
    # Get wealth gap indicators over time
    wealth_gap_data = session.exec(
        select(EconomicIndicator)
        .where(EconomicIndicator.indicator_type.in_(["wealth_gap", "gini_coefficient", "top_1_percent_share"]))
        .order_by(EconomicIndicator.date.asc())
    ).all()
    
    # Get policy events
    policy_events = session.exec(
        select(PolicyAction)
        .where(PolicyAction.policy_type.in_(["tax", "inflation", "economic", "regulation"]))
        .order_by(PolicyAction.date.asc())
    ).all()
    
    # Create timeline
    timeline = []
    for indicator in wealth_gap_data:
        # Find relevant policies around this time
        relevant_policies = [
            p for p in policy_events 
            if abs((p.date - indicator.date).days) <= 30  # Within 30 days
        ]
        
        timeline.append({
            "date": indicator.date,
            "indicator_type": indicator.indicator_type,
            "value": indicator.value,
            "related_policies": relevant_policies,
            "trend": calculate_trend(indicator, wealth_gap_data)
        })
    
    return {
        "timeline": timeline,
        "total_data_points": len(timeline),
        "wealth_gap_trend": calculate_overall_trend(wealth_gap_data)
    }


def analyze_business_performance(metrics: List[BusinessMetrics]) -> Dict[str, Any]:
    """Analyze business performance metrics."""
    if not metrics:
        return {}
    
    # Calculate profit margins
    profit_margins = []
    growth_rates = []
    closure_rates = []
    
    for i, metric in enumerate(metrics):
        profit_margin = (metric.total_profits / metric.total_sales) * 100 if metric.total_sales > 0 else 0
        profit_margins.append(profit_margin)
        
        if metric.closure_rate is not None:
            closure_rates.append(metric.closure_rate)
        
        # Calculate growth rate (compare with previous period)
        if i < len(metrics) - 1:
            prev_metric = metrics[i + 1]
            sales_growth = ((metric.total_sales - prev_metric.total_sales) / prev_metric.total_sales) * 100 if prev_metric.total_sales > 0 else 0
            growth_rates.append(sales_growth)
    
    return {
        "avg_profit_margin": sum(profit_margins) / len(profit_margins) if profit_margins else 0,
        "avg_growth_rate": sum(growth_rates) / len(growth_rates) if growth_rates else 0,
        "avg_closure_rate": sum(closure_rates) / len(closure_rates) if closure_rates else 0,
        "total_businesses": len(metrics),
        "latest_metrics": metrics[0] if metrics else None
    }


def calculate_trend(current_indicator: EconomicIndicator, all_indicators: List[EconomicIndicator]) -> str:
    """Calculate trend direction for an indicator."""
    same_type = [i for i in all_indicators if i.indicator_type == current_indicator.indicator_type]
    
    if len(same_type) < 2:
        return "insufficient_data"
    
    # Find current indicator in the list
    current_idx = next((i for i, ind in enumerate(same_type) if ind.date == current_indicator.date), -1)
    
    if current_idx <= 0:
        return "insufficient_data"
    
    # Compare with previous values
    prev_values = [same_type[i].value for i in range(max(0, current_idx - 3), current_idx)]
    if not prev_values:
        return "insufficient_data"
    
    prev_avg = sum(prev_values) / len(prev_values)
    
    if current_indicator.value > prev_avg * 1.05:
        return "increasing"
    elif current_indicator.value < prev_avg * 0.95:
        return "decreasing"
    else:
        return "stable"


def calculate_overall_trend(indicators: List[EconomicIndicator]) -> str:
    """Calculate overall trend for wealth gap indicators."""
    if len(indicators) < 2:
        return "insufficient_data"
    
    # Compare first half with second half
    mid_point = len(indicators) // 2
    first_half = indicators[:mid_point]
    second_half = indicators[mid_point:]
    
    first_avg = sum(i.value for i in first_half) / len(first_half)
    second_avg = sum(i.value for i in second_half) / len(second_half)
    
    if second_avg > first_avg * 1.05:
        return "widening"
    elif second_avg < first_avg * 0.95:
        return "narrowing"
    else:
        return "stable"
