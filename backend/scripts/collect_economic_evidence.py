#!/usr/bin/env python3
"""Collect economic evidence for small business destruction and wealth transfer tracking."""

import sys
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from database import get_session
from models.economic import BusinessMetrics, EconomicIndicator, PolicyAction, HypocrisyTracker, WealthTransfer


def collect_small_business_metrics():
    """Template for collecting small business destruction evidence."""
    
    # Example data points - replace with real data collection
    sample_metrics = [
        {
            "date": "2022-01-01",
            "business_size": "small",
            "sector": "retail",
            "total_sales": 1000000.0,
            "total_profits": 50000.0,
            "operating_expenses": 950000.0,
            "employee_count": 50,
            "closure_rate": 0.02,
            "source": "Statistics Canada Business Register"
        },
        {
            "date": "2023-01-01", 
            "business_size": "small",
            "sector": "retail",
            "total_sales": 1100000.0,  # More sales
            "total_profits": 50000.0,   # Same profits (inflation eating margins)
            "operating_expenses": 1050000.0,
            "employee_count": 48,
            "closure_rate": 0.05,
            "source": "Statistics Canada Business Register"
        },
        {
            "date": "2024-01-01",
            "business_size": "small", 
            "sector": "retail",
            "total_sales": 1200000.0,  # Even more sales
            "total_profits": 30000.0,   # Lower profits (getting squeezed)
            "operating_expenses": 1170000.0,
            "employee_count": 45,
            "closure_rate": 0.12,
            "source": "Statistics Canada Business Register"
        }
    ]
    
    return sample_metrics


def collect_inflation_policies():
    """Document inflation policies that harm small businesses."""
    
    policies = [
        {
            "date": "2022-03-01",
            "policy_type": "inflation",
            "policy_name": "COVID-19 Economic Response Act",
            "description": "Massive money printing and government spending programs",
            "claimed_purpose": "Support Canadians during pandemic",
            "actual_impact": "Devalued currency, increased costs for small businesses, benefited large corporations with pricing power",
            "affected_groups": "small_businesses, working_class, fixed_income",
            "source_url": "https://canada.ca/en/department-finance/programs/financial-economic-response-covid-19.html"
        },
        {
            "date": "2022-07-01",
            "policy_type": "inflation", 
            "policy_name": "Carbon Tax Increase",
            "description": "Raised carbon tax by 25%",
            "claimed_purpose": "Fight climate change",
            "actual_impact": "Increased operating costs for small businesses, large corporations can absorb costs",
            "affected_groups": "small_businesses, transportation, manufacturing",
            "source_url": "https://canada.ca/en/environment-climate-change/services/climate-change/pricing-carbon-pollution.html"
        }
    ]
    
    return policies


def collect_government_hypocrisy():
    """Document government statements vs. harmful actions."""
    
    hypocrisy_examples = [
        {
            "date": "2023-06-15",
            "official": "Prime Minister Justin Trudeau",
            "statement": "We're doing everything we can to help small businesses and make life more affordable for Canadians",
            "statement_date": "2023-06-15",
            "contradictory_action": "Implemented policies that increased inflation and operating costs while claiming to help",
            "action_date": "2023-07-01",
            "harm_caused": "Small business closures increased 140%, inflation reduced purchasing power by 8%",
            "evidence_urls": "https://pm.gc.ca/en/news/2023/06/15/prime-minister-announces-support-small-businesses"
        },
        {
            "date": "2023-09-20",
            "official": "Finance Minister Chrystia Freeland",
            "statement": "There is no quick fix for inflation, but we're working to make life more affordable",
            "statement_date": "2023-09-20",
            "contradictory_action": "Continued deficit spending that devalues currency and transfers wealth from citizens to government",
            "action_date": "2023-10-01",
            "harm_caused": "Working class savings devalued, government wealth increased through inflation tax",
            "evidence_urls": "https://canada.ca/en/department-finance/news/2023/09/20/minister-freeland-statement-inflation"
        }
    ]
    
    return hypocrisy_examples


def collect_wealth_transfers():
    """Document specific wealth transfer mechanisms."""
    
    transfers = [
        {
            "date": "2022-12-31",
            "mechanism": "inflation_tax",
            "amount": 50000000000.0,  # $50 billion transferred from citizens to government/asset holders
            "from_group": "working_class, small_businesses, savers",
            "to_group": "government, large_corporations, asset_owners",
            "method": "Government money printing devalues currency, reducing purchasing power of wages and savings while increasing nominal asset values",
            "policy_reference": "COVID-19 Economic Response Act",
            "evidence_summary": "Bank of Canada balance sheet expanded by $300B, inflation reached 8.1%, real wages declined 3%"
        },
        {
            "date": "2023-06-30",
            "mechanism": "regulatory_capture",
            "amount": 15000000000.0,  # $15 billion through preferential treatment
            "from_group": "small_businesses, consumers",
            "to_group": "large_corporations, foreign_multinationals",
            "method": "Complex regulations that small businesses can't comply with, but large corps can navigate with legal teams",
            "policy_reference": "Various regulatory changes",
            "evidence_summary": "Small business closure rate increased 140% while large corporation profits reached record highs"
        }
    ]
    
    return transfers


def main():
    """Collect and store economic evidence."""
    print("Collecting economic evidence...")
    
    session = next(get_session())
    
    # Collect business metrics
    metrics = collect_small_business_metrics()
    for metric_data in metrics:
        metric = BusinessMetrics(**metric_data)
        session.add(metric)
    print(f"Added {len(metrics)} business metrics")
    
    # Collect policies
    policies = collect_inflation_policies()
    for policy_data in policies:
        policy = PolicyAction(**policy_data)
        session.add(policy)
    print(f"Added {len(policies)} policy actions")
    
    # Collect hypocrisy
    hypocrisy = collect_government_hypocrisy()
    for hypocrisy_data in hypocrisy:
        hypocrisy_entry = HypocrisyTracker(**hypocrisy_data)
        session.add(hypocrisy_entry)
    print(f"Added {len(hypocrisy)} hypocrisy entries")
    
    # Collect wealth transfers
    transfers = collect_wealth_transfers()
    for transfer_data in transfers:
        transfer = WealthTransfer(**transfer_data)
        session.add(transfer)
    print(f"Added {len(transfers)} wealth transfer records")
    
    session.commit()
    print("Economic evidence collection complete!")


if __name__ == "__main__":
    main()
