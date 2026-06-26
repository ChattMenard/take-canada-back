#!/usr/bin/env python3
"""
Enter pre-pandemic connection evidence into the Veritas database.
"""

import sys
sys.path.insert(0, '/home/x99/Desktop/FUCK/backend')

from datetime import date
from app.database import get_session
from app.models.government_wealth import (
    OfficialAssetDeclaration, AssetHolding, BusinessInterest,
    PolicyDecision, FinancialTransaction, PolicyTransactionCorrelation,
    GovernmentContract, ConflictAssessment,
    calculate_correlation_score
)
from decimal import Decimal

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_status(msg, level="info"):
    color = GREEN if level == "success" else YELLOW if level == "warning" else RED
    print(f"{color}[{level.upper()}]{RESET} {msg}")

def main():
    print_status("Starting pre-pandemic connection evidence database population...", "info")
    session = next(get_session())

    try:
        # ========================================================================
        # PRE-PANDEMIC CONTRACTS & FUNDING
        # ========================================================================
        print_status("Entering pre-pandemic contracts and funding...", "info")

        pre_pandemic_contracts = [
            GovernmentContract(
                contract_number="PENN-CELLSCRIPT-2016",
                department="University of Pennsylvania (Private Institution)",
                contractor_name="Cellscript LLC / mRNA RiboTherapeutics",
                contract_value=Decimal("1000000000.00"),
                award_date=date(2016, 12, 20),
                procurement_method="exclusive_license",
                official_involvement="Penn exclusively licensed Kariko/Weissman mRNA patents to Cellscript; Cellscript sublicensed to Moderna (June 2017) and BioNTech (July 2017) BEFORE pandemic"
            ),
            GovernmentContract(
                contract_number="MODERNA-DARPA-2013",
                department="Defense Advanced Research Projects Agency (DARPA)",
                contractor_name="Moderna Therapeutics",
                contract_value=Decimal("25000000.00"),
                award_date=date(2013, 10, 2),
                procurement_method="grant",
                official_involvement="DARPA ADEPT-PROTECT: mRNA platform for 'known and unknown emerging infectious diseases and engineered biological threats'"
            ),
            GovernmentContract(
                contract_number="MODERNA-DARPA-2013-SEED",
                department="Defense Advanced Research Projects Agency (DARPA)",
                contractor_name="Moderna Therapeutics",
                contract_value=Decimal("1400000.00"),
                award_date=date(2013, 3, 22),
                procurement_method="grant",
                official_involvement="Initial DARPA award for 'modified RNA technology for production of antibodies for immune prophylaxis'"
            ),
            GovernmentContract(
                contract_number="MODERNA-GATES-2016",
                department="Bill & Melinda Gates Foundation",
                contractor_name="Moderna Therapeutics",
                contract_value=Decimal("100000000.00"),
                award_date=date(2016, 1, 1),
                procurement_method="grant_framework",
                official_involvement="Global health framework agreement; up to $100M for mRNA infectious disease projects; $20M initial for HIV antibodies"
            ),
            GovernmentContract(
                contract_number="NIAID-MODERNA-2019",
                department="National Institute of Allergy and Infectious Diseases (NIAID/NIH)",
                contractor_name="Moderna Therapeutics",
                contract_value=Decimal("0"),
                award_date=date(2019, 12, 16),
                procurement_method="joint_ownership_agreement",
                official_involvement="'mRNA coronavirus vaccine candidates developed and jointly-owned by NIAID and Moderna' transferred to UNC Dec 12, 2019 - 19 days before first COVID case"
            ),
            GovernmentContract(
                contract_number="CEPI-CUREVAC-2019",
                department="Coalition for Epidemic Preparedness Innovations (CEPI)",
                contractor_name="CureVac AG",
                contract_value=Decimal("34000000.00"),
                award_date=date(2019, 2, 1),
                procurement_method="grant",
                official_involvement="$34M for portable 'RNA Printer' mRNA vaccine manufacturing facility; CEPI founded 2017 with Gates/Wellcome/WEF"
            ),
            GovernmentContract(
                contract_number="ACUITAS-ARBUTUS-LNP",
                department="Canadian Courts (Patent Dispute)",
                contractor_name="Acuitas Therapeutics / Arbutus Biopharma",
                contract_value=Decimal("1000000000.00"),
                award_date=date(2018, 1, 1),
                procurement_method="litigation_settlement",
                official_involvement="Arbutus seeking 'hundreds of millions, if not billions' in royalties from Pfizer/BioNTech for UBC-developed LNP technology"
            ),
        ]
        session.add_all(pre_pandemic_contracts)
        session.flush()
        print_status(f"Pre-pandemic contracts entered ({len(pre_pandemic_contracts)} contracts)", "success")

        # ========================================================================
        # KEY OFFICIALS / RESEARCHERS
        # ========================================================================
        print_status("Entering key researcher declarations...", "info")

        kariko_decl = OfficialAssetDeclaration(
            official_name="Dr. Katalin Karikó",
            position="Senior VP, BioNTech / Adjunct Professor, Penn (former)",
            declaration_date=date(2023, 10, 1),
            file_path="/evidence/kariko_patent_income_cms_disclosure.pdf"
        )
        session.add(kariko_decl)
        session.flush()

        kariko_assets = [
            AssetHolding(
                declaration_id=kariko_decl.id,
                asset_type="intellectual_property_royalties",
                description="mRNA modification patents licensed to Moderna and BioNTech via Penn/Cellscript",
                value_range="$100M - $500M",
                acquisition_date=date(2005, 8, 23),
                policy_sensitive=True
            ),
        ]
        session.add_all(kariko_assets)

        weissman_decl = OfficialAssetDeclaration(
            official_name="Dr. Drew Weissman",
            position="Professor, Perelman School of Medicine, University of Pennsylvania",
            declaration_date=date(2023, 10, 1),
            file_path="/evidence/weissman_patent_income_cms_disclosure.pdf"
        )
        session.add(weissman_decl)
        session.flush()

        weissman_assets = [
            AssetHolding(
                declaration_id=weissman_decl.id,
                asset_type="intellectual_property_royalties",
                description="mRNA modification patents licensed to Moderna and BioNTech via Penn/Cellscript",
                value_range="$100M - $500M",
                acquisition_date=date(2005, 8, 23),
                policy_sensitive=True
            ),
        ]
        session.add_all(weissman_assets)

        cullis_decl = OfficialAssetDeclaration(
            official_name="Dr. Pieter Cullis",
            position="Professor, University of British Columbia / Chairman, Acuitas Therapeutics",
            declaration_date=date(2021, 1, 1),
            file_path="/evidence/cullis_ubc_acuitas_disclosure.pdf"
        )
        session.add(cullis_decl)
        session.flush()

        cullis_business = [
            BusinessInterest(
                declaration_id=cullis_decl.id,
                company_name="Acuitas Therapeutics Inc.",
                ownership_percentage=Decimal("100"),
                role="chairman",
                sector="biotechnology",
                policy_sensitive=True,
                establishment_date=date(2009, 1, 1)
            ),
            BusinessInterest(
                declaration_id=cullis_decl.id,
                company_name="Arbutus Biopharma (formerly Tekmira/Inex)",
                ownership_percentage=Decimal("0"),
                role="co_founder",
                sector="biotechnology",
                policy_sensitive=True,
                establishment_date=date(1990, 1, 1)
            ),
        ]
        session.add_all(cullis_business)

        baric_decl = OfficialAssetDeclaration(
            official_name="Dr. Ralph Baric",
            position="William R. Kenan Jr. Distinguished Professor, UNC Chapel Hill",
            declaration_date=date(2019, 12, 12),
            file_path="/evidence/baric_moderna_niaid_mta_dec2019.pdf"
        )
        session.add(baric_decl)
        session.flush()

        baric_conflict = ConflictAssessment(
            declaration_id=baric_decl.id,
            assessment_date=date(2019, 12, 12),
            policy_matter="Received mRNA coronavirus vaccine candidates from Moderna/NIAID 19 days before first COVID case; leading gain-of-function coronavirus researcher",
            conflict_found=True,
            resolution="Collaborated with NIAID/Moderna on vaccine testing; also collaborated with Wuhan Institute of Virology on coronavirus research"
        )
        session.add(baric_conflict)

        fauci_decl = OfficialAssetDeclaration(
            official_name="Dr. Anthony Fauci",
            position="Director, NIAID (1984-2022)",
            declaration_date=date(2017, 1, 10),
            file_path="/evidence/fauci_georgetown_speech_jan2017.pdf"
        )
        session.add(fauci_decl)
        session.flush()

        print_status("Key researcher declarations entered", "success")

        # ========================================================================
        # POLICY DECISIONS
        # ========================================================================
        print_status("Entering pre-pandemic policy decisions...", "info")

        policies = [
            PolicyDecision(
                policy_id="EVENT-201-2019",
                policy_title="Event 201: Global Pandemic Simulation (Johns Hopkins, WEF, Gates Foundation)",
                decision_type="simulation_exercise",
                proposal_date=date(2019, 10, 18),
                announcement_date=date(2019, 10, 18),
                implementation_date=date(2019, 10, 18),
                affected_sectors='["healthcare", "media", "finance", "technology", "government"]',
                decision_makers='["Johns Hopkins Center for Health Security", "World Economic Forum", "Bill & Melinda Gates Foundation", "George Gao", "Avril Haines"]'
            ),
            PolicyDecision(
                policy_id="CRIMSON-CONTAGION-2019",
                policy_title="Crimson Contagion: HHS Pandemic Functional Exercise",
                decision_type="simulation_exercise",
                proposal_date=date(2019, 1, 1),
                announcement_date=date(2019, 8, 16),
                implementation_date=date(2019, 8, 16),
                affected_sectors='["healthcare", "government", "manufacturing", "supply_chain"]',
                decision_makers='["HHS", "19 federal agencies", "12 states", "CDC", "FEMA"]'
            ),
            PolicyDecision(
                policy_id="DARPA-ADEPT-2013",
                policy_title="DARPA ADEPT-PROTECT: mRNA Platform for Biological Threats",
                decision_type="military_research",
                proposal_date=date(2013, 3, 22),
                announcement_date=date(2013, 10, 2),
                implementation_date=date(2013, 10, 2),
                affected_sectors='["biotechnology", "military", "pharmaceutical", "national_security"]',
                decision_makers='["DARPA", "Moderna", "U.S. Department of Defense"]'
            ),
            PolicyDecision(
                policy_id="MODERNA-1273-2020",
                policy_title="Moderna mRNA-1273 COVID Vaccine Development",
                decision_type="emergency_authorization",
                proposal_date=date(2020, 1, 10),
                announcement_date=date(2020, 3, 16),
                implementation_date=date(2020, 12, 18),
                affected_sectors='["healthcare", "pharmaceutical", "biotechnology"]',
                decision_makers='["Moderna", "NIAID", "FDA", "Operation Warp Speed"]'
            ),
        ]
        session.add_all(policies)
        session.flush()
        print_status(f"Policy decisions entered ({len(policies)} policies)", "success")

        # ========================================================================
        # CORRELATIONS
        # ========================================================================
        print_status("Calculating pre-pandemic correlations...", "info")

        # Patent licensing -> Pandemic profit
        patent_transaction = FinancialTransaction(
            transaction_id="PATENT-PRE-PANDEMIC-2017",
            person_name="Cellscript LLC / University of Pennsylvania",
            relationship_to_official="patent_holder",
            transaction_type="establish",
            asset_description="Exclusive mRNA patents sublicensed to Moderna and BioNTech in 2017, generating $1B+ in royalties after pandemic",
            transaction_date=date(2017, 6, 26),
            transaction_value=Decimal("1000000000.00"),
            asset_sector="biotechnology_patents",
            policy_sensitive=True
        )
        session.add(patent_transaction)
        session.flush()

        # DARPA funding -> Moderna success
        darpa_transaction = FinancialTransaction(
            transaction_id="DARPA-MODERNA-2013",
            person_name="Moderna Therapeutics",
            relationship_to_official="military_contractor",
            transaction_type="establish",
            asset_description="DARPA-funded mRNA platform became basis for COVID-19 vaccine generating $100B+ in sales",
            transaction_date=date(2013, 10, 2),
            transaction_value=Decimal("25000000.00"),
            asset_sector="military_biotechnology",
            policy_sensitive=True
        )
        session.add(darpa_transaction)
        session.flush()

        # Event 201 -> Pandemic response
        event201_transaction = FinancialTransaction(
            transaction_id="EVENT-201-2019",
            person_name="Johns Hopkins / WEF / Gates Foundation",
            relationship_to_official="simulation_organizers",
            transaction_type="establish",
            asset_description="Pandemic simulation in October 2019 practiced censorship, lockdowns, and vaccine distribution 2 months before COVID",
            transaction_date=date(2019, 10, 18),
            transaction_value=Decimal("0"),
            asset_sector="pandemic_preparedness",
            policy_sensitive=True
        )
        session.add(event201_transaction)
        session.flush()

        # Moderna/NIAID Dec 2019 agreement
        niaid_transaction = FinancialTransaction(
            transaction_id="NIAID-MODERNA-DEC2019",
            person_name="NIAID and Moderna",
            relationship_to_official="joint_researchers",
            transaction_type="establish",
            asset_description="Jointly-owned mRNA coronavirus vaccine candidates transferred to Ralph Baric at UNC 19 days before first COVID case",
            transaction_date=date(2019, 12, 12),
            transaction_value=Decimal("0"),
            asset_sector="biodefense_research",
            policy_sensitive=True
        )
        session.add(niaid_transaction)
        session.flush()

        # Correlate with Moderna vaccine policy
        moderna_policy = session.query(PolicyDecision).filter(PolicyDecision.policy_id == "MODERNA-1273-2020").first()
        if moderna_policy:
            score = calculate_correlation_score(
                time_advantage_days=-45,
                value_impact_percent=95.0,
                sector_match=True,
                decision_maker_involved=True
            )
            corr = PolicyTransactionCorrelation(
                policy_id=moderna_policy.id,
                transaction_id=niaid_transaction.id,
                time_advantage_days=-45,
                value_impact_percent=Decimal("95.00"),
                sector_match=True,
                decision_maker_involved=True,
                correlation_score=Decimal(str(score)),
                confidence_level="critical"
            )
            session.add(corr)

            score2 = calculate_correlation_score(
                time_advantage_days=-2555,
                value_impact_percent=90.0,
                sector_match=True,
                decision_maker_involved=True
            )
            corr2 = PolicyTransactionCorrelation(
                policy_id=moderna_policy.id,
                transaction_id=darpa_transaction.id,
                time_advantage_days=-2555,
                value_impact_percent=Decimal("90.00"),
                sector_match=True,
                decision_maker_involved=True,
                correlation_score=Decimal(str(score2)),
                confidence_level="high"
            )
            session.add(corr2)

        # Commit all changes
        session.commit()
        print_status("All pre-pandemic connection evidence committed to database!", "success")

        # Print summary
        print("\n" + "="*60)
        print("PRE-PANDEMIC CONNECTIONS DATABASE POPULATION SUMMARY")
        print("="*60)

        from sqlalchemy import func
        total_contracts = session.query(GovernmentContract).count()
        total_decls = session.query(OfficialAssetDeclaration).count()
        total_conflicts = session.query(ConflictAssessment).count()
        total_business = session.query(BusinessInterest).count()
        total_policies = session.query(PolicyDecision).count()
        total_correlations = session.query(PolicyTransactionCorrelation).count()

        print(f"Total Government Contracts: {total_contracts}")
        print(f"Total Official Declarations: {total_decls}")
        print(f"Total Conflict Assessments: {total_conflicts}")
        print(f"Total Business Interests: {total_business}")
        print(f"Total Policy Decisions: {total_policies}")
        print(f"Total Correlations: {total_correlations}")
        print("="*60)

        return 0

    except Exception as e:
        session.rollback()
        print_status(f"Error: {e}", "error")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())
