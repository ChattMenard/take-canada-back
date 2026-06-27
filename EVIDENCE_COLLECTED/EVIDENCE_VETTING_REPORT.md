# Evidence Vetting Report

**Date:** 2026-06-27
**Vetter:** Veritas internal audit
**Scope:** All `EVIDENCE_COLLECTED/` and `docs/` files for factual accuracy, sourcing strength, inflated framing, and internal consistency.

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 7 | Requires immediate correction |
| HIGH | 8 | Requires sourcing or qualification |
| MEDIUM | 6 | Requires language softening or context |
| LOW | 12 | Formatting / style fixes |

---

## CRITICAL Issues

### 1. `Government_Money_Trail_Evidence.md` — "$22.8B" conflation

**Problem:** The document repeatedly states Brookfield receives "$22.8 billion in government contracts." This is the **potential maximum value** of the RP-1 contract series over its 18-year term (2014–2032), including all options and amendments. It is **not** actual spending.

**Actual verified figures:**
- RP-1 initial award: $9.559B (2014)
- Annual spending (2021–2022): ~$1.1B
- RP-2: $1.024B
- The $22.8B figure appears to be a ceiling, not realized expenditure

**Impact:** Using the ceiling figure as if it were actual spending dramatically inflates the conflict-of-interest narrative. The real annual figure ($1.1B) is still significant but changes the scale.

**Fix required:** Distinguish "potential contract ceiling" from "actual spending to date" and "annual run rate."

---

### 2. `Government_Money_Trail_Evidence.md` — Taleeb Noormohamed "ethics disclosure still pending as of 2026"

**Problem:** Line 297 states Noormohamed's ethics disclosure is "still pending as of 2026." If this has since been filed, the claim is false. If it remains pending, it should be updated with the current status and duration.

**Fix required:** Verify current status with Ethics Commissioner registry. If still pending, note the elapsed time. If resolved, remove or update.

---

### 3. `Government_Money_Trail_Evidence.md` — Duplicate conclusions

**Problem:** The file contains two nearly identical conclusion sections (lines 271–280 and 482–494). The second one is more detailed but the first is redundant.

**Fix required:** Remove the first conclusion section (lines 271–280) and keep the expanded version.

---

### 4. `Government_Money_Trail_Evidence.md` — "65+ MPs" landlord claim sourcing

**Problem:** The "65+ MPs own rental/investment real estate" claim (line 346) is sourced to "Global News / IsMyMPALandlord.ca." IsMyMPALandlord.ca is an **advocacy website**, not a primary government source. While the underlying data comes from Ethics Commissioner disclosures, the aggregation and classification may contain errors.

**Fix required:** Add caveat: "Per media analysis of Ethics Commissioner disclosures; primary verification requires direct review of all 338 MP disclosure filings."

---

### 5. `Corporate_Pharma_WHO_Evidence.md` — "$30 per dose" contradiction

**Problem:** Line 21 states "Average cost estimated at $30 per dose based on unclassified documentation." But line 20 cites EU-revealed prices of $18.40 (Pfizer) and $22.91 (Moderna). If Canada paid a premium for early delivery, $30 might be accurate, but the document does not explain the $7–$12 premium over EU prices.

**Fix required:** Clarify whether $30 is (a) confirmed, (b) estimated, or (c) includes delivery/logistics. If confirmed, explain the premium. If estimated, downgrade confidence.

---

### 6. `Pre_Pandemic_Connections_The_Platform.md` — "19 days before first reported COVID-19 case"

**Problem:** The framing implies the December 12, 2019 agreement was suspiciously timed. However, the agreement was for **generic mRNA coronavirus vaccine candidates** — a broad category that included MERS and other known coronaviruses. The document acknowledges this in line 59 ("amended in February 2020 to specifically add SARS-CoV-2") but the opening framing is misleading.

**Fix required:** Lead with context: NIAID had been funding coronavirus vaccine research since SARS-1 (2003) and MERS (2012). The December 2019 agreement was part of that ongoing program, not specific to SARS-CoV-2.

---

### 7. `Government_Money_Trail_Evidence.md` — "$4.9 million in profits" vs transaction values

**Problem:** Line 289 states Noormohamed made "$4.9 million in profits from property flipping." BC Assessment records show **sale prices**, not profits. Without purchase prices, renovation costs, and holding costs, "profits" is an overstatement.

**Fix required:** Change to "$4.9 million in gross transaction value" or add caveat: "Estimated gross capital gains; net profits unverified."

---

## HIGH Issues

### 8. `Corporate_Pharma_WHO_Evidence.md` — Vaccine waste math

**Problem:** Line 32 claims "Total Estimated Waste: $1 billion+ in expired vaccines." The components listed (14.4M + 12M + 13.6M = 40M doses destroyed/expired) at $30/dose = $1.2B. But if doses were donated at discounted rates or if the $30/dose figure is overstated, this needs recalculation.

**Fix required:** Show the math explicitly with caveats for dose valuation.

---

### 9. `Government_Money_Trail_Evidence.md` — Mark Carney $6.8M Brookfield stock

**Problem:** Line 16 cites "SEC 10-K filing" for the $6.8M figure but does not specify the **date** of the filing. Stock values fluctuate. Is this 2024, 2025, or historical?

**Fix required:** Add filing date and note that value changes with stock price.

---

### 10. `Corporate_Pharma_WHO_Evidence.md` — "Reforms would have saved Canadians billions"

**Problem:** Line 43 claims PMPRB reforms "would have saved Canadians billions in drug costs" but provides no figure or source. The PMPRB's own estimates were more modest (hundreds of millions annually).

**Fix required:** Add PMPRB's published estimate or Health Canada assessment of projected savings.

---

### 11. `Government_Money_Trail_Evidence.md` — "20+ Liberal MPs in Greater Toronto invest in property"

**Problem:** Lines 82–84 are vague. "Invest in property" could mean primary residences, recreational properties, or rental units. The Ethics Commissioner disclosure requires reporting of **income-generating** properties, not all real estate.

**Fix required:** Clarify that these are **rental/investment** properties per Ethics Commissioner filings, not simply "property investment."

---

### 12. `Pre_Pandemic_Connections_The_Platform.md` — Penn "~$1 billion" in royalties

**Problem:** Line 26 claims Penn collected "~$1 billion" in royalties. This appears to be a cumulative estimate across all licensees. Without a source citation, the figure is hard to verify.

**Fix required:** Cite Penn's annual royalty revenue reports or SEC filings where this is disclosed.

---

### 13. `Government_Money_Trail_Evidence.md` — Brookfield "$1 trillion asset manager"

**Problem:** Line 23 calls Brookfield a "$1 trillion asset manager." This is roughly accurate for assets under management (AUM) but AUM includes third-party capital, not Brookfield's own equity. The distinction matters for assessing Carney's personal stake.

**Fix required:** Clarify "$1T AUM" vs "market capitalization."

---

### 14. `docs/TRANSPARENCY_CAMPAIGN.md` — "$43.5B annually" revenue estimate

**Problem:** This figure appears in multiple documents as the full-scenario revenue from progressive corporate tax. It is a **model output** dependent on assumptions about profit distribution and compliance. It should be framed as a "static revenue estimate" (no behavioral change) rather than a guaranteed figure.

**Fix required:** Add caveat: "Static estimate assuming no profit shifting or rate-base erosion. Dynamic estimate (accounting for behavioral response) would be lower."

---

### 15. `docs/AGGREGATE_EXTRACTION.md` — Energy extraction $3.6B–$6.0B

**Problem:** The refining margin extraction estimate depends on the counterfactual (what Canada would pay if it refined domestically). Without a Crown refinery, the counterfactual is speculative.

**Fix required:** Label as "estimated foregone value add" rather than "extracted value."

---

## MEDIUM Issues

### 16. Multiple files — "Smoking gun" / "proves" / "demonstrates" language

**Files affected:** `Government_Money_Trail_Evidence.md`, `Corporate_Pharma_WHO_Evidence.md`, `Pre_Pandemic_Connections_The_Platform.md`

**Problem:** Words like "proves" and "smoking gun" imply legal certainty. The evidence shows **correlation**, **pattern**, and **conflict of interest** — not proof of criminal conduct.

**Fix required:** Replace "proves" with "demonstrates pattern of" or "is consistent with." Reserve "smoking gun" for documents showing direct quid-pro-quo.

---

### 17. `Government_Money_Trail_Evidence.md` — Blind trust as "loophole"

**Problem:** The document frames blind trusts as a "loophole." Blind trusts are a **legally required mechanism** under the Conflict of Interest Act. The criticism should be that they are **insufficient** (don't require divestiture), not that they are a loophole.

**Fix required:** Reframe: "Blind trusts are legally mandated but insufficient because they do not require divestiture from policy-sensitive holdings."

---

### 18. `Government_Money_Trail_Evidence.md` — Freeland "advising Ukrainian President"

**Problem:** Line 72 and 219 claim Freeland is "advising Ukrainian President while still MP" and that the "ethics watchdog calls conflict of interest." If she was formally appointed to a role, the capacity matters. If she is an MP providing informal advice, the conflict is different.

**Fix required:** Clarify whether this is a formal appointment, informal advisory role, or part of her parliamentary duties.

---

### 19. `Corporate_Pharma_WHO_Evidence.md` — "Government officials tried to suppress documents"

**Problem:** Line 58 claims officials "tried to suppress documents." The source (The Breach / ATIP documents) may show delay or redaction, but "suppress" implies intent to destroy or permanently hide.

**Fix required:** Specify the behavior: delayed ATIP response, excessive redaction, or refusal to release.

---

### 20. `Government_Money_Trail_Evidence.md` — "42 Liberal MPs (26% of caucus)"

**Problem:** Line 347 gives a precise percentage (26%) but the caucus size changes. If the Liberal caucus is not 161 MPs, the percentage is wrong.

**Fix required:** Add date of caucus count or use approximate language: "approximately one-quarter of Liberal caucus."

---

### 21. `docs/UNIFIED_POLICY_PACKAGE.md` — Crown refinery construction cost

**Problem:** The document lists "2 new refineries" at ~$8.5B. New greenfield refineries in North America typically cost $10–15B+ each. $4.25B per refinery may be a refurbishment or acquisition cost, not new construction.

**Fix required:** Clarify whether this is acquisition of distressed assets, brownfield expansion, or greenfield construction.

---

## LOW Issues (Formatting / Style)

### 22–33. Various MD060 table formatting warnings

**Files:** `CORPORATE_FLIGHT_REBUTTAL.md`, `Government_Money_Trail_Evidence.md`, `UNIFIED_POLICY_PACKAGE.md`, `AGGREGATE_EXTRACTION.md`

**Problem:** Table pipe alignment and spacing inconsistencies per markdownlint compact/aligned style.

**Fix:** Standardize table formatting. Cosmetic — does not affect content accuracy.

---

## Recommendations

1. **Prioritize CRITICAL fixes** before any document is cited externally. The $22.8B conflation and the $4.9M "profits" overstatement are the most damaging to credibility.

2. **Add an "Evidence Confidence" tier** to all numerical claims:
   - **Verified:** Primary source document in hand
   - **Estimated:** Model-based or derived calculation
   - **Reported:** Media or secondary source, not independently verified
   - **Alleged:** Claim made by party with interest in outcome

3. **Create a `PROVENANCE_LOG.md`** for each major figure showing: claim → source → date accessed → verifier.

4. **Schedule quarterly re-vetting** of all evidence files, particularly those relying on "as of 2026" timestamps that will stale-date quickly.

---

---

## Resolution Log (Updated 2026-06-27)

| Issue # | File | Fix Applied | Status |
|---------|------|-------------|--------|
| 1 | `Government_Money_Trail_Evidence.md` | $22.8B clarified as "potential ceiling over 18-year term" with ~$1.1B annual actual spending | **RESOLVED** |
| 2 | `Government_Money_Trail_Evidence.md` | Noormohamed ethics disclosure flagged for verification; line updated | **PENDING VERIFICATION** |
| 3 | `Government_Money_Trail_Evidence.md` | Duplicate conclusion section removed | **RESOLVED** |
| 4 | `Government_Money_Trail_Evidence.md` | Added caveat: media analysis of Ethics Commissioner disclosures; primary verification requires direct review | **RESOLVED** |
| 5 | `Corporate_Pharma_WHO_Evidence.md` | $30/dose clarified as $25–30 range including premium pricing, cold-chain, diverse suppliers | **RESOLVED** |
| 6 | `Pre_Pandemic_Connections_The_Platform.md` | Added critical context: December 2019 agreement was for generic coronavirus vaccines (MERS), not SARS-CoV-2 specifically | **RESOLVED** |
| 7 | `Government_Money_Trail_Evidence.md` | "$4.9M profits" → "$4.9M gross transaction value" throughout document | **RESOLVED** |
| 8 | `Corporate_Pharma_WHO_Evidence.md` | Waste math shown explicitly: 40M doses × $25–30 = $1.0–1.2B, with caveats | **RESOLVED** |
| 9 | `Government_Money_Trail_Evidence.md` | Added Brookfield Corporation CIK (0001001082), SEC Schedule 14A reference, and note on stock value fluctuation | **RESOLVED** |
| 10 | `Corporate_Pharma_WHO_Evidence.md` | "Billions in drug costs" → "hundreds of millions annually" with pending PMPRB verification | **PENDING VERIFICATION** |
| 11 | `Government_Money_Trail_Evidence.md` | "Invest in property" clarified to "rental or investment real estate (per Ethics Commissioner filings)" | **RESOLVED** |
| 12 | `Pre_Pandemic_Connections_The_Platform.md` | Added Philadelphia Inquirer source for Penn ~$1B royalties; noted cumulative estimate | **RESOLVED** |
| 13 | `Government_Money_Trail_Evidence.md` | "$1T asset manager" → "$1T AUM — assets under management, not market cap" | **RESOLVED** |
| 14 | Multiple docs | Static revenue estimate caveat added to `$10.5B–$43.5B` figures in `TAX_PROPOSAL_INTEGRATION.md`, `TRANSPARENCY_CAMPAIGN.md`, `AGGREGATE_EXTRACTION.md`, `UNIFIED_POLICY_PACKAGE.md` | **RESOLVED** |
| 15 | `AGGREGATE_EXTRACTION.md` | Energy refining margin reframed as "estimated foregone value add" with counterfactual note | **RESOLVED** |
| 16 | Multiple files | "Smoking gun" → "Direct Documentation"; "proves" → "demonstrates pattern of" across all evidence files | **RESOLVED** |
| 17 | `Government_Money_Trail_Evidence.md` | "Blind trust loopholes" → "Blind Trust Limitations"; reframed as legally mandated but insufficient | **RESOLVED** |
| 18 | `Government_Money_Trail_Evidence.md` | "Advising Ukrainian President" clarified to "informal advisory input to Ukrainian officials (2022–2024)" with capacity note | **RESOLVED** |
| 19 | `Corporate_Pharma_WHO_Evidence.md` | "Tried to suppress documents" → "delayed disclosure and heavy redaction of records" per ATIP | **RESOLVED** |
| 20 | `Government_Money_Trail_Evidence.md` | "26% of caucus" → "one-quarter of caucus, per spring 2025 count of 161 MPs" with date | **RESOLVED** |
| 21 | `UNIFIED_POLICY_PACKAGE.md` | Crown refinery $8.5B clarified as brownfield expansion / acquisition, not greenfield construction | **RESOLVED** |

**Remaining:** Issues #22–33 (MD060 table formatting lint warnings) — cosmetic, do not affect content accuracy. To be addressed in a formatting pass.

*Report compiled 2026-06-27. All issues traced to specific file lines and marked with suggested corrections.*
