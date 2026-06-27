# Corporate Housing Influence Framework

## Following Big Corporate Money in the Housing Crisis

This framework tracks how corporate interests, developers, and financial institutions influence housing policy to maximize profits while creating affordable housing shortages.

---

## Core Hypothesis

**Corporate Profit-Driven Housing Crisis:** Systematic analysis of how corporate interests manipulate housing policy, land use, and development regulations to create artificial scarcity and maximize profits, leading to:

1. **Policy Capture:** Housing policies designed to benefit corporate developers over public needs
2. **Land Banking:** Corporate hoarding of developable land to drive up prices
3. **Regulatory Arbitrage:** Zoning and building codes that favor large corporate developers
4. **Financialization:** Housing treated as financial asset rather than human need

---

## Evidence Collection Framework

### 1. Corporate Developer Influence Tracking

**Data Points to Collect:**
- Corporate political donations to housing policy makers
- Lobbying registrations and activities
- Developer participation in policy consultations
- Revolving door employment between government and developers
- Corporate media campaigns on housing policy

**Evidence Structure:**
```python
class CorporateHousingInfluence(BaseModel):
    corporation_name: str
    industry_sector: str  # development, finance, real estate
    political_donations: List[PoliticalDonation]
    lobbying_activities: List[LobbyingActivity]
    policy_consultations: List[PolicyConsultation]
    revolving_door_hires: List[RevolvingDoorHire]
    media_campaigns: List[MediaCampaign]

class PoliticalDonation(BaseModel):
    recipient: str  # politician, party, riding association
    amount: Decimal
    date: date
    donation_type: str  # corporate, individual, executive
    housing_policy_relevance: float  # 0-1 score
```

### 2. Housing Policy vs Corporate Profit Analysis

**Key Correlations to Track:**
- Policy changes that benefit specific corporate developers
- Zoning changes that increase land values for corporate holdings
- Building code changes that favor large corporate builders
- Tax policies that benefit corporate real estate investment

**Data Sources:**
- Municipal zoning decisions and meeting minutes
- Provincial housing policy announcements
- Federal housing program designs
- Corporate financial reports and investor calls

**Analysis Framework:**
```python
class HousingPolicyCorporateImpact(BaseModel):
    policy_id: str
    policy_type: str  # zoning, building code, tax, subsidy
    announcement_date: date
    implementation_date: date
    affected_corporations: List[str]
    profit_impact_estimates: List[ProfitImpact]
    policy_maker_connections: List[PolicyConnection]

class ProfitImpact(BaseModel):
    corporation: str
    impact_type: str  # land_value, development_cost, market_access
    pre_policy_value: Decimal
    post_policy_value: Decimal
    impact_duration_months: int
    confidence_level: str
```

### 3. Land Banking and Speculation Tracking

**Focus Areas:**
- Corporate land holdings in high-demand areas
- Land banking by institutional investors
- Speculative holding patterns vs. development timelines
- Foreign corporate ownership of developable land

**Evidence Collection:**
- Land registry records and corporate ownership structures
- Development applications and approval timelines
- Property tax assessments and valuation changes
- Corporate real estate investment fund filings

**Land Banking Analysis:**
```python
class LandBankingActivity(BaseModel):
    parcel_id: str
    corporate_owner: str
    acquisition_date: date
    acquisition_price: Decimal
    current_assessed_value: Decimal
    zoning_status: str
    development_status: str
    holding_period_months: int
    speculation_score: float  # 0-1 probability
```

### 4. Affordable Housing Policy Sabotage Tracking

**Patterns to Identify:**
- Opposition to inclusionary zoning policies
- Lobbying against rent control measures
- Campaigns against social housing development
- Regulatory barriers to affordable housing construction

**Evidence Types:**
- Industry association lobbying records
- Media campaigns and op-eds
- Political campaign contributions
- Policy consultation submissions

---

## ATIP Request Templates

### Template 1: CMHC - Housing Policy Development

**Subject:** Access to Information Request — Housing Policy Development and Corporate Influence

To: ATIP Coordinator, Canada Mortgage and Housing Corporation

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All housing policy development documents from January 1, 2015 to present, including:
   - Policy development processes and stakeholder consultations
   - Impact assessments of policy options on different market segments
   - Corporate developer participation in policy consultations
   - Analysis of policy impacts on corporate vs. public interests

2. All communications with corporate developers regarding:
   - Housing program design and implementation
   - Policy changes affecting development profitability
   - Regulatory requirements and compliance costs
   - Market analysis and housing supply projections

3. All records of corporate influence on housing policy, including:
   - Lobbying activities and meetings
   - Political donations and their correlation to policy decisions
   - Revolving door employment patterns
   - Industry association influence campaigns

4. All analyses of housing affordability impacts, including:
   - Corporate profit trends vs. housing affordability metrics
   - Land banking effects on housing supply
   - Development cost breakdowns and profit margins
   - Market concentration and competition analysis

This request relates to understanding how corporate interests influence housing policy and affect housing affordability.

### Template 2: Finance Ministry - Housing Finance Policy

**Subject:** Access to Information Request — Housing Finance Policy and Corporate Financial Interests

To: ATIP Coordinator, Department of Finance

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All housing finance policy documents from January 1, 2015 to present, including:
   - Mortgage insurance policy development
   - Tax policy affecting housing investment
   - Financial institution regulations for housing lending
   - Housing market intervention strategies

2. All communications with financial institutions regarding:
   - Housing market policies and regulations
   - Mortgage insurance and risk management
   - Housing investment tax treatment
   - Market intervention impacts on profitability

3. All analyses of corporate financial interests in housing, including:
   - Bank profitability from mortgage lending
   - Real estate investment trust (REIT) growth and tax treatment
   - Institutional investor housing market participation
   - Financialization of housing impacts

4. All policy impact assessments regarding:
   - Effects on corporate vs. individual housing market participants
   - Housing affordability impacts of financial policies
   - Market concentration and competition effects
   - Financial stability vs. housing affordability trade-offs

This request relates to understanding how financial corporations influence housing policy and affect housing affordability.

### Template 3: Municipal Governments - Zoning and Development

**Subject:** Access to Information Request — Zoning Decisions and Corporate Developer Influence

To: ATIP Coordinator, [Major City] Municipal Government

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All zoning and development decisions from January 1, 2015 to present, including:
   - Zoning bylaw amendments and their justifications
   - Development application approvals and rejections
   - Planning committee meeting minutes and decisions
   - Developer consultation processes and outcomes

2. All communications with corporate developers regarding:
   - Specific development proposals and applications
   - Zoning changes and planning decisions
   - Development fee structures and exemptions
   - Infrastructure requirements and cost allocations

3. All records of corporate influence on development decisions, including:
   - Lobbying activities and meeting records
   - Political donations and their correlation to development approvals
   - Campaign contributions to municipal officials
   - Industry association influence activities

4. All analyses of development impacts, including:
   - Corporate profit margins on approved developments
   - Land value increases from zoning changes
   - Affordable housing contributions vs. market-rate units
   - Development cost breakdowns and profit allocations

This request relates to understanding how corporate developers influence municipal development decisions and affect housing affordability.

---

## Analysis Framework

### 1. Profit vs Affordability Correlation Analysis

**Key Metrics:**
- Corporate developer profit margins over time
- Housing affordability index trends
- Land value inflation rates
- Development cost increases vs. income growth

**Analysis Methods:**
- Time series analysis of profit vs. affordability trends
- Geographic analysis of development patterns
- Market concentration analysis
- Policy impact assessment on corporate profits

### 2. Policy Influence Network Analysis

**Connection Mapping:**
- Corporate developer to policy maker connections
- Political donation patterns to housing policy decisions
- Lobbying activity outcomes
- Revolving door employment patterns

**Influence Metrics:**
- Network centrality of corporate developers
- Policy decision correlation with corporate interests
- Media campaign effectiveness
- Policy consultation participation rates

### 3. Land Banking Impact Assessment

**Analysis Dimensions:**
- Land holding periods vs. development timelines
- Speculative holding patterns
- Land value inflation from holding
- Development cost impacts of land banking

**Impact Measurement:**
- Housing supply reduction from land banking
- Price inflation from artificial scarcity
- Development delay costs
- Market concentration effects

---

## Housing Affordability Evidence Templates

### Template 4: Housing Market Data Analysis

**Subject:** Access to Information Request — Housing Market Data and Corporate Market Share

To: ATIP Coordinator, Statistics Canada

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All housing market data from January 1, 2015 to present, including:
   - Housing price indexes by region and property type
   - Housing affordability metrics and trends
   - Market share data for corporate vs. individual developers
   - Rental market data and vacancy rates

2. All data on corporate housing market participation, including:
   - Corporate ownership of residential properties
   - Institutional investor housing market activities
   - Real estate investment trust (REIT) portfolios
   - Foreign corporate investment in housing

3. All housing supply and demand analysis, including:
   - Housing construction starts and completions
   - Development pipeline and approval timelines
   - Land banking and speculative holding patterns
   - Housing market concentration metrics

4. All affordability impact assessments, including:
   - Housing cost burden trends by income level
   - Homeownership accessibility trends
   - Rental affordability trends
   - Housing market inequality measures

This request relates to understanding corporate influence on housing markets and housing affordability.

---

## Public Interest Framing

### Legitimate Areas of Inquiry

**Accountability Questions:**
- Do corporate housing profits come at the expense of housing affordability?
- Are housing policies designed to benefit corporate developers over public needs?
- Is land banking by corporations creating artificial housing scarcity?
- Are financial institutions treating housing as investment rather than human need?

**Evidence-Based Messaging:**
- "Analyzing corporate influence on housing policy and affordability"
- "Understanding the relationship between developer profits and housing costs"
- "Examining land banking impacts on housing supply and prices"
- "Ensuring housing policy serves public interest rather than corporate profit"

**Avoid:**
- Allegations of illegal activity without evidence
- Generalizations about all corporations
- Speculation about motives or intent
- Conspiracy theories about housing markets

---

## Success Metrics

### Evidence Collection Success
- ATIP response rate: >80%
- Corporate influence data completeness: >85%
- Housing market data coverage: >90%
- Policy analysis reproducibility: 100%

### Analysis Quality
- Statistical significance: p < 0.05
- Peer review publication: Academic journals
- Expert validation: Independent review
- Methodology transparency: Full documentation

### Public Impact
- Policy discussions referencing findings
- Housing advocacy groups using evidence
- Media coverage: Major outlets
- Citizen engagement: Increased awareness

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-4)
- File priority ATIP requests for housing policy data
- Set up corporate influence tracking database
- Begin housing market data collection

### Phase 2: Data Collection (Weeks 5-8)
- Process received policy and corporate data
- Collect housing market and affordability data
- Map corporate influence networks

### Phase 3: Analysis (Weeks 9-12)
- Conduct profit vs. affordability analysis
- Complete policy influence assessment
- Analyze land banking impacts

### Phase 4: Public Engagement (Weeks 13-16)
- Release evidence-based findings
- Engage housing advocates and policymakers
- Support citizen advocacy efforts

---

## Case Study: Edmonton Infill — Destroying Affordable Housing to Build "Affordable" Housing

### The Property

- **Type:** Post-WWII single-family home, 2-bedroom, double-wide, corner lot
- **Features:** Full backyard, firepit, mature shade trees, single-door garage
- **Rent:** $1,700/month (bills included)
- **Status:** Demolished for 8-unit row house infill

### What Replaces It

| | Original House | Replacement Row House |
|---|---|---|
| Units | 1 | 8 |
| Bedrooms | 2 | Mostly 1-2 bed |
| Rent per unit | $1,700 (bills included) | $1,350-$1,500 (bills extra) |
| Total lot rent | $1,700 | $10,800-$12,000 |
| Yard | Full corner lot | None |
| Garage | Single-door | None |
| Trees | Mature shade trees | New sod |
| Community continuity | Resident gardener, sunflowers | Transient rental population |

### The "Affordability" Lie

The city and developers frame infill as increasing affordable housing supply. The reality:

- **The demolished unit WAS affordable.** $1,700 for a 2BR with yard and bills included is below-market in Edmonton 2026.
- **The replacement units are NOT cheaper.** A 1-bedroom at $1,350 without bills is not more affordable than a 2-bedroom at $1,700 with bills included — it's a worse deal per square foot, per bedroom, and per amenity.
- **8 people now pay what 1 person paid.** The landlord extracts 6-7x the revenue from the same lot. The city gets 4x the property tax. The tenant gets a smaller box.
- **The premium housing stock is permanently lost.** Post-war homes on corner lots with mature trees cannot be rebuilt. Once demolished, that quality of life is gone forever.

### The Tax Transfer

Edmonton's multi-residential tax premium (15% above base residential rate) is being phased out over 5 years via a 7-6 council vote. By 2026 (year 3), the premium is roughly 6% remaining.

| | Old House | New 8-Unit Rental |
|---|---|---|
| Assessed value | ~$500K | ~$1.75-2.0M (GIM method) |
| Tax rate | 1.036% | ~1.10% (phasing DOWN) |
| Annual tax | ~$5,200 | ~$19,000-22,000 |
| Tax per unit | N/A | ~$2,400-2,750 |
| **Tax revenue for city** | **~$5,200** | **~$19,000-22,000** |

The city collects **4x more tax** from the same footprint while the **tax rate on those units actively decreases**. Single-family homeowners who do not sell to infill developers absorb the shifted burden.

### Who Benefits

| Stakeholder | Benefit |
|-------------|---------|
| **Developer** | Construction profit + sale to landlord |
| **Landlord** | 6-7x revenue from same lot; GIM-assessed property |
| **City** | 4x property tax revenue; density targets met |
| **Tenant** | Smaller unit, no yard, no garage, no trees, similar or higher all-in cost |
| **Community** | Loss of established residents, gardens, neighborhood character |

### Why Infill? Not Affordability — Developer Math

The city frames infill as "sustainable growth." The actual driver is simpler:

- **Farmland at the urban fringe is expensive** — assembly, servicing, road extensions, utility hookups, environmental assessments, and municipal contributions make greenfield development costly and slow.
- **Existing lots inside the city are cheap and already serviced** — water, sewer, roads, and power exist. The landowner already holds title. No environmental review, no growth management, no regional planning fights.
- **Upzoning turns a $500K lot into a $1.75M revenue machine** — the developer pays market rate for a single-family lot, demolishes the house, and builds 8 units. The profit margin on density far exceeds the margin on greenfield sprawl.

Infill is not chosen because it serves tenants better. It is chosen because **it is cheaper for the developer and more profitable per square foot of land.** The city enables this by:
- Fast-tracking demolition permits
- Eliminating community consultation on "as-of-right" density
- Phasing out the tax premium that might have made infill less attractive
- Refusing to mandate below-market units or displacement compensation

### The Policy Mechanism

1. **Zoning upzoning** allows 8 units where 1 stood
2. **GIM assessment** (income approach) values the property based on rent potential, not replacement cost — inflating assessed value
3. **Tax premium phase-out** shifts burden to single-family homeowners
4. **No affordable housing requirement** — no mandatory below-market units, no community land trust, no public benefit
5. **Demolition permits** are rubber-stamped; no displacement mitigation

### The Systematic Elimination of Below-Market Housing

This is not an accident. It is the logical outcome of a system that treats "below market" as a defect to be corrected rather than a public good to be protected.

Every policy lever works in the same direction:

- **Upzoning** destroys below-market stock by making demolition profitable
- **GIM assessment** prices housing based on maximum rent extraction, not replacement cost
- **Tax premium phase-out** removes the disincentive that once made speculation less attractive
- **No displacement protection** means tenants have no standing when their home is demolished
- **No below-market replacement requirements** means every demolished affordable unit is gone forever

The result is a city where nothing is allowed to exist below the market rate. Every lot, every unit, every square foot is pushed toward the maximum revenue it can generate. The post-war home with a yard and a garage and a $1,700 rent is not preserved — it is converted into eight $1,350 boxes because the aggregate revenue is higher.

This is not housing policy. It is **market-rate enforcement** wearing the language of affordability.

### Verdict

This is not affordable housing policy. It is **density-for-profit policy** dressed in affordability language. The existing affordable unit is destroyed. The replacement units cost more per square foot. The landlord, developer, and city treasury benefit. The tenant and community lose.

---

## Conclusion

The Corporate Housing Influence Framework provides systematic tools for examining how corporate interests shape housing policy to maximize profits while creating affordable housing shortages. By focusing on documented evidence, statistical analysis, and transparent methodology, this framework enables citizens to understand the relationship between corporate profits and housing affordability.

This approach maintains Veritas standards for evidence-based accountability while addressing legitimate public interest questions about corporate influence in housing markets and policy.

---

*Document prepared for Veritas corporate housing influence tracking.*
*Updated: June 26, 2026*
