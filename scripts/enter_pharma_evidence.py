#!/usr/bin/env python3
"""
Enter corporate pharma/WHO evidence into the Veritas database.
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
    print_status("Starting pharma/WHO evidence database population...", "info")
    session = next(get_session())

    try:
        # ========================================================================
        # EVIDENCE 1: Pfizer COVID Vaccine Contracts
        # ========================================================================
        print_status("Entering Pfizer contract evidence...", "info")

        pfizer_contracts = [
            GovernmentContract(
                contract_number="COVID-VACC-PFIZER-2020",
                department="Public Services and Procurement Canada / Public Health Agency of Canada",
                contractor_name="Pfizer-BioNTech",
                contract_value=Decimal("5000000000.00"),
                award_date=date(2020, 7, 1),
                procurement_method="sole-source",
                official_involvement="Minister Anita Anand cited confidentiality clauses preventing disclosure"
            ),
            GovernmentContract(
                contract_number="COVID-VACC-MODERNA-2020",
                department="Public Services and Procurement Canada / Public Health Agency of Canada",
                contractor_name="Moderna",
                contract_value=Decimal("2000000000.00"),
                award_date=date(2020, 8, 1),
                procurement_method="sole-source",
                official_involvement="Confidential pricing; EU accidentally revealed $22.91/dose"
            ),
            GovernmentContract(
                contract_number="VACCINECONNECT-DELOITTE",
                department="Public Health Agency of Canada",
                contractor_name="Deloitte Inc.",
                contract_value=Decimal("60000000.00"),
                award_date=date(2021, 1, 1),
                procurement_method="competitive",
                official_involvement="$60M system to track vaccine distribution; had delays and problems"
            ),
            GovernmentContract(
                contract_number="COVID-VACC-WASTAGE",
                department="Public Health Agency of Canada",
                contractor_name="Multiple (Pfizer, Moderna, AstraZeneca, etc.)",
                contract_value=Decimal("1000000000.00"),
                award_date=date(2020, 12, 1),
                procurement_method="advance_purchase_agreement",
                official_involvement="Auditor General: 32.5M doses in inventory worth ~$1B expired"
            ),
        ]
        session.add_all(pfizer_contracts)
        session.flush()
        print_status(f"Pfizer/COVID contracts entered ({len(pfizer_contracts)} contracts)", "success")

        # ========================================================================
        # EVIDENCE 2: Health Minister Duclos Declaration
        # ========================================================================
        print_status("Entering Jean-Yves Duclos evidence...", "info")

        duclos_decl = OfficialAssetDeclaration(
            official_name="Jean-Yves Duclos",
            position="Minister of Health",
            declaration_date=date(2021, 10, 1),
            file_path="/evidence/duclos_ethics_disclosure.pdf"
        )
        session.add(duclos_decl)
        session.flush()

        duclos_conflicts = [
            ConflictAssessment(
                declaration_id=duclos_decl.id,
                assessment_date=date(2022, 11, 28),
                policy_matter="Intervened to suspend drug price reforms after pharmaceutical lobbying",
                conflict_found=True,
                resolution="Letter to PMPRB described as 'indistinguishable from pharma lobby talking points'; reforms suspended indefinitely"
            ),
        ]
        session.add_all(duclos_conflicts)
        print_status(f"Duclos evidence entered (Declaration ID: {duclos_decl.id})", "success")

        # ========================================================================
        # EVIDENCE 3: IMC Paid StatCan Reports
        # ========================================================================
        print_status("Entering IMC-StatCan evidence...", "info")

        imc_contract = GovernmentContract(
            contract_number="IMC-STATCAN-2020",
            department="Statistics Canada",
            contractor_name="Innovative Medicines Canada",
            contract_value=Decimal("161072.00"),
            award_date=date(2020, 1, 1),
            procurement_method="sole-source",
            official_involvement="Pharma lobby paid StatCan for reports used in lobbying without disclosure; IMC had final approval over indicators"
        )
        session.add(imc_contract)
        session.flush()
        print_status("IMC-StatCan evidence entered", "success")

        # ========================================================================
        # EVIDENCE 4: Revolving Door - Thomas Digby
        # ========================================================================
        print_status("Entering revolving door evidence...", "info")

        digby_decl = OfficialAssetDeclaration(
            official_name="Thomas J. Digby",
            position="Chairperson, Patented Medicine Prices Review Board (PMPRB)",
            declaration_date=date(2023, 2, 1),
            file_path="/evidence/digby_pmprb_appointment.pdf"
        )
        session.add(digby_decl)
        session.flush()

        digby_business = [
            BusinessInterest(
                declaration_id=digby_decl.id,
                company_name="Private Intellectual Property Law Practice (Pharma/Biotech)",
                ownership_percentage=Decimal("100.00"),
                role="owner",
                sector="legal_services_pharma",
                policy_sensitive=True,
                establishment_date=date(1998, 1, 1)
            ),
        ]
        session.add_all(digby_business)

        digby_conflict = ConflictAssessment(
            declaration_id=digby_decl.id,
            assessment_date=date(2023, 2, 1),
            policy_matter="Appointed to chair drug price regulator after 25+ years as pharma IP lawyer",
            conflict_found=True,
            resolution="Board member resigned citing concerns about panel independence; IMC welcomed appointment"
        )
        session.add(digby_conflict)
        print_status(f"Digby evidence entered (Declaration ID: {digby_decl.id})", "success")

        # ========================================================================
        # EVIDENCE 5: Pamela Fralick - Former Health Canada to Pharma Lobby
        # ========================================================================
        print_status("Entering Pamela Fralick evidence...", "info")

        fralick_decl = OfficialAssetDeclaration(
            official_name="Pamela Fralick",
            position="Former President, Innovative Medicines Canada",
            declaration_date=date(2022, 1, 1),
            file_path="/evidence/fralick_lobby_registry.pdf"
        )
        session.add(fralick_decl)
        session.flush()

        fralick_business = [
            BusinessInterest(
                declaration_id=fralick_decl.id,
                company_name="Innovative Medicines Canada",
                ownership_percentage=Decimal("0"),
                role="president",
                sector="pharmaceutical_lobby",
                policy_sensitive=True,
                establishment_date=date(2022, 1, 1)
            ),
        ]
        session.add_all(fralick_business)
        print_status(f"Fralick evidence entered", "success")

        # ========================================================================
        # EVIDENCE 6: Bettina Hamelin - Former NSERC to Pharma Lobby
        # ========================================================================
        print_status("Entering Bettina Hamelin evidence...", "info")

        hamelin_decl = OfficialAssetDeclaration(
            official_name="Bettina Hamelin",
            position="President and CEO, Innovative Medicines Canada",
            declaration_date=date(2024, 1, 1),
            file_path="/evidence/hamelin_lobby_registry.pdf"
        )
        session.add(hamelin_decl)
        session.flush()

        hamelin_business = [
            BusinessInterest(
                declaration_id=hamelin_decl.id,
                company_name="Innovative Medicines Canada",
                ownership_percentage=Decimal("0"),
                role="president_ceo",
                sector="pharmaceutical_lobby",
                policy_sensitive=True,
                establishment_date=date(2024, 1, 1)
            ),
        ]
        session.add_all(hamelin_business)
        print_status(f"Hamelin evidence entered", "success")

        # ========================================================================
        # EVIDENCE 7: WHO Funding
        # ========================================================================
        print_status("Entering WHO funding evidence...", "info")

        who_contracts = [
            GovernmentContract(
                contract_number="WHO-CONTRIBUTION-2024",
                department="Global Affairs Canada / Health Canada",
                contractor_name="World Health Organization",
                contract_value=Decimal("55070443.00"),
                award_date=date(2024, 1, 1),
                procurement_method="voluntary_contribution",
                official_involvement="Canada 5th largest Member State donor; $55M in 2024"
            ),
            GovernmentContract(
                contract_number="WHO-CONTRIBUTION-2025",
                department="Global Affairs Canada / Health Canada",
                contractor_name="World Health Organization",
                contract_value=Decimal("58089144.00"),
                award_date=date(2025, 1, 1),
                procurement_method="voluntary_contribution",
                official_involvement="$58M in 2025; total $900M+ over 10 years"
            ),
            GovernmentContract(
                contract_number="WHO-PANDEMIC-AGREEMENT",
                department="Global Affairs Canada / Health Canada",
                contractor_name="World Health Organization",
                contract_value=Decimal("0"),
                award_date=date(2025, 5, 1),
                procurement_method="treaty_adoption",
                official_involvement="Canada adopted WHO Pandemic Agreement May 2025; no parliamentary debate or vote"
            ),
        ]
        session.add_all(who_contracts)
        session.flush()
        print_status(f"WHO funding evidence entered ({len(who_contracts)} records)", "success")

        # ========================================================================
        # POLICY DECISIONS
        # ========================================================================
        print_status("Entering policy decisions...", "info")

        policies = [
            PolicyDecision(
                policy_id="DRUG-PRICE-REFORM-2017",
                policy_title="Patented Medicine Prices Review Board reforms to lower drug prices",
                decision_type="regulatory",
                proposal_date=date(2017, 1, 1),
                announcement_date=date(2017, 5, 1),
                implementation_date=date(2022, 12, 1),
                affected_sectors='["pharmaceutical", "healthcare", "insurance"]',
                decision_makers='["Jean-Yves Duclos", "Health Minister", "PMPRB"]'
            ),
            PolicyDecision(
                policy_id="PHARMACARE-LIBNDP-2022",
                policy_title="Canada Pharmacare Act commitment under Liberal-NDP agreement",
                decision_type="legislative",
                proposal_date=date(2022, 3, 22),
                announcement_date=date(2022, 3, 22),
                implementation_date=date(2023, 12, 31),
                affected_sectors='["pharmaceutical", "healthcare", "insurance"]',
                decision_makers='["Justin Trudeau", "Jagmeet Singh", "Health Minister"]'
            ),
            PolicyDecision(
                policy_id="WHO-PANDEMIC-AGREEMENT-2025",
                policy_title="Adoption of WHO Pandemic Agreement (legally binding treaty)",
                decision_type="international_treaty",
                proposal_date=date(2024, 6, 1),
                announcement_date=date(2025, 5, 1),
                implementation_date=date(2025, 5, 1),
                affected_sectors='["healthcare", "international_relations", "sovereignty"]',
                decision_makers='["Global Affairs Minister", "Health Minister", "Prime Minister"]'
            ),
        ]
        session.add_all(policies)
        session.flush()
        print_status(f"Policy decisions entered ({len(policies)} policies)", "success")

        # ========================================================================
        # CORRELATIONS
        # ========================================================================
        print_status("Calculating correlations...", "info")

        # Lobbying -> Policy Block correlation
        lobby_transaction = FinancialTransaction(
            transaction_id="IMC-LOBBY-2022",
            person_name="Innovative Medicines Canada",
            relationship_to_official="lobbyist",
            transaction_type="establish",
            asset_description="150+ lobbying communications with Health Canada in 9 months; 3x increase over average",
            transaction_date=date(2022, 11, 1),
            transaction_value=Decimal("0"),
            asset_sector="pharmaceutical_lobbying",
            policy_sensitive=True
        )
        session.add(lobby_transaction)
        session.flush()

        # Pfizer contract correlation
        pfizer_transaction = FinancialTransaction(
            transaction_id="PFIZER-CONTRACT-2020",
            person_name="Pfizer-BioNTech",
            relationship_to_official="corporate_contractor",
            transaction_type="establish",
            asset_description="COVID vaccine supply contract with confidential pricing clauses",
            transaction_date=date(2020, 7, 1),
            transaction_value=Decimal("5000000000.00"),
            asset_sector="pharmaceutical",
            policy_sensitive=True
        )
        session.add(pfizer_transaction)
        session.flush()

        drug_policy = session.query(PolicyDecision).filter(PolicyDecision.policy_id == "DRUG-PRICE-REFORM-2017").first()
        if drug_policy:
            score = calculate_correlation_score(
                time_advantage_days=0,
                value_impact_percent=100.0,
                sector_match=True,
                decision_maker_involved=True
            )
            corr = PolicyTransactionCorrelation(
                policy_id=drug_policy.id,
                transaction_id=lobby_transaction.id,
                time_advantage_days=0,
                value_impact_percent=Decimal("100.00"),
                sector_match=True,
                decision_maker_involved=True,
                correlation_score=Decimal(str(score)),
                confidence_level="high"
            )
            session.add(corr)

        # WHO funding -> Treaty adoption
        who_transaction = FinancialTransaction(
            transaction_id="WHO-FUNDING-2025",
            person_name="World Health Organization",
            relationship_to_official="international_organization",
            transaction_type="establish",
            asset_description="Canada adopted legally binding WHO Pandemic Agreement after contributing $900M+ over 10 years",
            transaction_date=date(2025, 5, 1),
            transaction_value=Decimal("900000000.00"),
            asset_sector="international_health",
            policy_sensitive=True
        )
        session.add(who_transaction)
        session.flush()

        who_policy = session.query(PolicyDecision).filter(PolicyDecision.policy_id == "WHO-PANDEMIC-AGREEMENT-2025").first()
        if who_policy:
            score = calculate_correlation_score(
                time_advantage_days=0,
                value_impact_percent=75.0,
                sector_match=True,
                decision_maker_involved=True
            )
            corr2 = PolicyTransactionCorrelation(
                policy_id=who_policy.id,
                transaction_id=who_transaction.id,
                time_advantage_days=0,
                value_impact_percent=Decimal("75.00"),
                sector_match=True,
                decision_maker_involved=True,
                correlation_score=Decimal(str(score)),
                confidence_level="high"
            )
            session.add(corr2)

        print_status("Correlation analysis complete", "success")

        # Commit all changes
        session.commit()
        print_status("All pharma/WHO evidence committed to database!", "success")

        # Print summary
        print("\n" + "="*60)
        print("PHARMA/WHO EVIDENCE DATABASE POPULATION SUMMARY")
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
