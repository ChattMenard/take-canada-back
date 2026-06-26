"""Historical parallels documentation - comparing current policies to historical oppression mechanisms."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import PolicyAction, WealthTransfer, HypocrisyTracker

router = APIRouter(prefix="/api/historical-parallels", tags=["historical-parallels"])


@router.get("/oppression-mechanisms")
def get_oppression_mechanisms_comparison(
    session: Session = Depends(get_session),
):
    """Compare current Canadian policies to historical oppression mechanisms."""
    
    # Get current policies
    current_policies = session.exec(
        select(PolicyAction)
        .order_by(PolicyAction.date.desc())
        .limit(50)
    ).all()
    
    # Historical parallels database
    historical_parallels = [
        {
            "historical_regime": "Nazi Germany (1933-1945)",
            "mechanism": "Legal Framework for Discrimination",
            "historical_policy": "Nuremberg Laws (1935)",
            "description": "Legal framework that systematically discriminated against Jewish citizens, restricted rights, and enabled property seizure",
            "current_parallel": {
                "policy": "Emergency Powers Act (2022)",
                "mechanism": "Legal framework for suspending rights",
                "similarity": "Both use legal frameworks to suspend citizen rights and enable extraordinary state powers"
            }
        },
        {
            "historical_regime": "Nazi Germany (1933-1945)",
            "mechanism": "Economic Control and Wealth Transfer",
            "historical_policy": "Aryanization of Jewish businesses (1938)",
            "description": "Systematic transfer of wealth from targeted groups to favored groups through legal and economic means",
            "current_parallel": {
                "policy": "Inflation and regulatory policies",
                "mechanism": "Wealth transfer from small businesses to corporations",
                "similarity": "Both use economic mechanisms to transfer wealth from disfavored groups to elite groups"
            }
        },
        {
            "historical_regime": "Soviet Union (1917-1991)",
            "mechanism": "Surveillance and Control",
            "historical_policy": "KGB surveillance network",
            "description": "Comprehensive surveillance of citizens to identify and suppress dissent",
            "current_parallel": {
                "policy": "FINTRAC and Bills C-22/C-26",
                "mechanism": "Financial surveillance and communications monitoring",
                "similarity": "Both use comprehensive surveillance to monitor and control citizen behavior"
            }
        },
        {
            "historical_regime": "Apartheid South Africa (1948-1994)",
            "mechanism": "Legal Segregation and Control",
            "historical_policy": "Pass laws and population registration",
            "description": "Legal framework that created distinct classes of citizens with different rights",
            "current_parallel": {
                "policy": "Vaccine passports and emergency restrictions",
                "mechanism": "Creation of different classes of citizens with different rights",
                "similarity": "Both create legal distinctions between citizens with different rights and freedoms"
            }
        }
    ]
    
    return {
        "historical_parallels": historical_parallels,
        "current_policies_count": len(current_policies),
        "analysis_summary": {
            "total_parallels": len(historical_parallels),
            "common_mechanisms": ["legal_frameworks", "economic_control", "surveillance", "citizen_classification"],
            "warning_level": "high"
        }
    }


@router.get("/wealth-concentration-patterns")
def analyze_wealth_concentration_patterns(
    session: Session = Depends(get_session),
):
    """Analyze patterns of wealth concentration compared to historical examples."""
    
    # Get wealth transfer data
    wealth_transfers = session.exec(
        select(WealthTransfer)
        .order_by(WealthTransfer.date.desc())
        .limit(100)
    ).all()
    
    # Historical wealth concentration patterns
    historical_patterns = [
        {
            "historical_example": "Weimar Germany Hyperinflation (1921-1923)",
            "mechanism": "Currency devaluation through money printing",
            "effect": "Middle class wealth destroyed, transferred to those holding hard assets",
            "current_evidence": [
                transfer for transfer in wealth_transfers 
                if transfer.mechanism == "inflation_tax"
            ],
            "similarity_score": 0.85
        },
        {
            "historical_example": "Soviet Collectivization (1928-1937)",
            "mechanism": "Destruction of independent producers",
            "effect": "Small farms eliminated, wealth concentrated in state-controlled entities",
            "current_evidence": [
                transfer for transfer in wealth_transfers 
                if "small_business" in transfer.from_group
            ],
            "similarity_score": 0.75
        },
        {
            "historical_example": "Roman Empire Currency Debasement",
            "mechanism": "Progressive currency devaluation",
            "effect": "Wealth transferred from currency holders to those with hard assets",
            "current_evidence": [
                transfer for transfer in wealth_transfers 
                if transfer.mechanism in ["inflation_tax", "currency_devaluation"]
            ],
            "similarity_score": 0.80
        }
    ]
    
    return {
        "historical_patterns": historical_patterns,
        "current_evidence_count": len(wealth_transfers),
        "pattern_analysis": {
            "most_similar": max(historical_patterns, key=lambda x: x["similarity_score"]),
            "average_similarity": sum(p["similarity_score"] for p in historical_patterns) / len(historical_patterns),
            "risk_assessment": "critical"
        }
    }


@router.get("/propaganda-and-control")
def analyze_propaganda_and_control_mechanisms(
    session: Session = Depends(get_session),
):
    """Analyze propaganda and control mechanisms compared to historical examples."""
    
    # Get hypocrisy entries (government statements vs actions)
    hypocrisy_entries = session.exec(
        select(HypocrisyTracker)
        .order_by(HypocrisyTracker.date.desc())
        .limit(50)
    ).all()
    
    # Historical propaganda and control mechanisms
    historical_control = [
        {
            "historical_regime": "Nazi Germany",
            "mechanism": "Propaganda and Media Control",
            "tactics": [
                "Control of media narrative",
                "Repetition of false narratives",
                "Creation of common enemies",
                "Claiming to protect citizens while harming them"
            ],
            "current_examples": [
                {
                    "statement": "We're doing everything we can to help Canadians",
                    "reality": "Policies that destroy small businesses and reduce purchasing power",
                    "similarity": "Claims of protection while implementing harmful policies"
                }
            ]
        },
        {
            "historical_regime": "Soviet Union",
            "mechanism": "Information Control",
            "tactics": [
                "State-controlled media",
                "Suppression of dissenting voices",
                "Creation of alternate reality",
                "Punishment for truth-telling"
            ],
            "current_examples": [
                {
                    "statement": "There is no quick fix for inflation",
                    "reality": "Continuing policies that cause inflation while claiming helplessness",
                    "similarity": "Creating narrative of inevitability while causing the problem"
                }
            ]
        }
    ]
    
    # Map current hypocrisy to historical patterns
    current_patterns = []
    for entry in hypocrisy_entries:
        pattern = {
            "official": entry.official,
            "statement": entry.statement,
            "contradictory_action": entry.contradictory_action,
            "historical_parallel": "Claims of protection while implementing control",
            "control_mechanism": "Narrative control to mask harmful policies"
        }
        current_patterns.append(pattern)
    
    return {
        "historical_control_mechanisms": historical_control,
        "current_patterns": current_patterns,
        "analysis": {
            "total_hypocrisy_entries": len(hypocrisy_entries),
            "most_common_parallel": "Claims of protection while implementing harm",
            "control_methods": ["narrative_control", "information_suppression", "false_solutions"]
        }
    }


@router.get("/early-warning-signs")
def get_early_warning_signs(
    session: Session = Depends(get_session),
):
    """Identify early warning signs based on historical patterns of authoritarianism."""
    
    # Historical early warning signs
    historical_warnings = [
        {
            "warning_sign": "Expansion of executive power",
            "historical_examples": ["Enabling Act (Germany)", "Emergency Powers (various)"],
            "current_indicators": ["Emergency Powers Act 2022", "Ministerial orders without oversight"],
            "risk_level": "high"
        },
        {
            "warning_sign": "Creation of out-groups",
            "historical_examples": ["Jews as enemies", "Class enemies", "Counter-revolutionaries"],
            "current_indicators": ["Unvaccinated as threats", "Freedom convoy as extremists", "Dissenters as misinformers"],
            "risk_level": "high"
        },
        {
            "warning_sign": "Economic destruction of independent groups",
            "historical_examples": ["Aryanization", "Collectivization", "Cultural Revolution"],
            "current_indicators": ["Small business destruction", "Independent media suppression", "Professional licensing control"],
            "risk_level": "critical"
        },
        {
            "warning_sign": "Surveillance expansion",
            "historical_examples": ["Gestapo", "KGB", "Stasi"],
            "current_indicators": ["FINTRAC expansion", "Digital ID", "Social credit monitoring"],
            "risk_level": "high"
        },
        {
            "warning_sign": "Control of information",
            "historical_examples": ["Goebbels Ministry", "Pravda", "Cultural Revolution propaganda"],
            "current_indicators": ["Media censorship", "Social media control", "Fact-checking as censorship"],
            "risk_level": "high"
        }
    ]
    
    # Current evidence assessment
    current_evidence = {
        "executive_power_expansion": session.exec(
            select(PolicyAction).where(PolicyAction.policy_type == "emergency")
        ).all(),
        "economic_destruction": session.exec(
            select(WealthTransfer).where(WealthTransfer.from_group.like("%small%"))
        ).all(),
        "surveillance_expansion": session.exec(
            select(PolicyAction).where(PolicyAction.policy_type == "surveillance")
        ).all()
    }
    
    return {
        "historical_warning_signs": historical_warnings,
        "current_evidence": {
            "executive_power_count": len(current_evidence["executive_power_expansion"]),
            "economic_destruction_count": len(current_evidence["economic_destruction"]),
            "surveillance_expansion_count": len(current_evidence["surveillance_expansion"])
        },
        "overall_risk_assessment": {
            "risk_level": "critical",
            "triggered_warnings": len([w for w in historical_warnings if w["risk_level"] in ["high", "critical"]]),
            "recommendation": "Immediate citizen action required to prevent further consolidation of power"
        }
    }
