# Government Wealth Tracking Framework

## Following the Money: Policy, Power, and Personal Enrichment

This framework extends the Veritas transparency campaign to track how government officials and their networks benefit from policy decisions, procurement contracts, and regulatory changes.

---

## Core Hypothesis

**"Policy-for-Profit" Pattern:** Government officials and their networks systematically position themselves to benefit from policy decisions they create, through:

1. **Timing Advantage:** Knowledge of upcoming policy changes before public announcement
2. **Procurement Influence:** Directing government contracts to connected entities
3. **Regulatory Arbitrage:** Creating regulations that benefit specific industries/individuals
4. **Asset Appreciation:** Policy decisions that increase value of held assets

---

## Evidence Collection Framework

### 1. Asset Declaration Tracking

**Data Points to Collect:**
- Initial asset declarations upon taking office
- Annual/periodic updates
- Spouse and dependent assets
- Business interests and holdings
- Real estate holdings
- Investment portfolios and timing

**ATIP Targets:**
- Office of the Conflict of Interest and Ethics Commissioner
- Treasury Board Secretariat
- Individual ministerial offices
- Parliamentary ethics committees

**Evidence Types:**
```python
class OfficialAssetDeclaration(BaseModel):
    official_name: str
    position: str
    declaration_date: date
    assets: List[AssetHolding]
    spouse_assets: List[AssetHolding]
    business_interests: List[BusinessInterest]
    real_estate: List[RealEstateHolding]
    previous_declaration_id: str  # For change tracking

class AssetHolding(BaseModel):
    asset_type: str  # stock, bond, real estate, business
    description: str
    value_range: str  # "$100,001-$250,000"
    acquisition_date: date
    disposition_date: Optional[date]
    policy_sensitive: bool
```

### 2. Policy Timing vs Investment Analysis

**Key Correlations to Track:**
- Stock purchases before regulatory changes
- Real estate acquisitions before zoning changes
- Business investments before procurement announcements
- Asset sales before negative policy announcements

**Data Sources:**
- Hansard (parliamentary proceedings) for policy discussions
- Regulatory Impact Analysis Statements (RIAS)
- Government contract announcements
- Stock market data and insider trading reports
- Land registry records

**Analysis Framework:**
```python
class PolicyInvestmentCorrelation(BaseModel):
    policy_announcement_date: date
    policy_type: str  # regulatory, procurement, tax, spending
    affected_sectors: List[str]
    official_involvement: str
    related_transactions: List[TransactionTiming]
    time_advantage_days: int
    value_impact_estimate: Decimal

class TransactionTiming(BaseModel):
    person_name: str
    relationship_to_official: str  # spouse, family member, business associate
    transaction_type: str  # buy, sell, establish
    asset_description: str
    transaction_date: date
    value: Decimal
    policy_correlation_score: float  # 0-1 probability
```

### 3. Procurement and Contract Tracking

**Focus Areas:**
- Contracts awarded to former colleagues/business associates
- Sole-source contracts without competitive bidding
- Contracts that expand after initial award
- Contracts to companies with recent political donations

**ATIP Templates:**
- Public Services and Procurement Canada contract awards
- Individual department procurement records
- Treasury Board contract approval documents
- Conflict of interest assessments for contracts

**Evidence Structure:**
```python
class GovernmentContract(BaseModel):
    contract_number: str
    department: str
    contractor_name: str
    contractor_ownership: List[OwnershipEntity]
    contract_value: Decimal
    award_date: date
    procurement_method: str  # competitive, sole-source, emergency
    official_involvement: str
    political_connections: List[PoliticalConnection]
    contract_amendments: List[ContractAmendment]

class OwnershipEntity(BaseModel):
    entity_name: str
    owners: List[PersonOrEntity]
    ownership_percentage: float
    government_connections: List[GovernmentConnection]
```

### 4. Family and Network Business Interests

**Tracking Framework:**
- Spouse business activities and directorships
- Children and extended family business interests
- Business partners and associates
- Corporate directorships and advisory roles
- Family investment portfolios and holdings
- Intergenerational wealth transfers

**Evidence Collection:**
- Corporate registries and director filings
- Business registration databases
- Professional association memberships
- Lobbying registration records
- Investment portfolio disclosures
- Trust and estate documents
- Family office structures

**Detailed Family Business Analysis:**
```python
class FamilyBusinessNetwork(BaseModel):
    central_official: str
    immediate_family: List[FamilyMember]
    extended_family: List[FamilyMember]
    business_associates: List[BusinessAssociate]
    family_investments: List[FamilyInvestment]
    wealth_transfers: List[WealthTransfer]

class FamilyMember(BaseModel):
    name: str
    relationship: str  # spouse, child, sibling, parent, in-law
    business_interests: List[BusinessInterest]
    directorships: List[Directorship]
    investment_portfolio: List[InvestmentHolding]
    government_connections: List[GovConnection]
    policy_sensitive_activities: List[PolicySensitiveActivity]

class BusinessInterest(BaseModel):
    company_name: str
    ownership_percentage: float
    role: str  # owner, director, officer, advisor
    sector: str
    policy_sensitive: bool
    revenue: Decimal
    establishment_date: date
    recent_growth: float

class InvestmentPortfolio(BaseModel):
    portfolio_owner: str
    holdings: List[InvestmentHolding]
    total_value: Decimal
    policy_sensitive_sectors: List[str]
    recent_transactions: List[PortfolioTransaction]
    fund_manager: str
    blind_trust: bool

class WealthTransfer(BaseModel):
    transfer_type: str  # gift, inheritance, trust, loan
    transferor: str
    transferee: str
    amount: Decimal
    date: date
    purpose: str
    policy_timing_correlation: float
```

---

## ATIP Request Templates

### Template 1: Conflict of Interest Commissioner - Asset Declarations

**Subject:** Access to Information Request — Minister Asset Declarations and Conflict Assessments

To: ATIP Coordinator, Office of the Conflict of Interest and Ethics Commissioner

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All asset declarations filed by Cabinet ministers from January 1, 2015 to present, including:
   - Initial declarations upon appointment
   - Annual updates
   - Spouse and dependent asset disclosures
   - Business interest declarations

2. All conflict of interest assessments conducted for ministers regarding:
   - Specific policy decisions
   - Procurement contracts
   - Regulatory changes
   - Cabinet discussions

3. All investigations or inquiries into potential conflicts of interest, including:
   - Complaints received
   - Investigations initiated
   - Findings and outcomes
   - Recommendations made

4. All communications between the Commissioner and ministerial offices regarding:
   - Potential conflicts
   - Compliance requirements
   - Enforcement actions

This request relates to understanding how government officials manage potential conflicts between public duties and private interests.

### Template 2: Public Services - Contract Awards

**Subject:** Access to Information Request — Government Contract Awards and Procurement Decisions

To: ATIP Coordinator, Public Services and Procurement Canada

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All contract awards over $100,000 from January 1, 2015 to present, including:
   - Contract details and specifications
   - Bidding process documentation
   - Evaluation criteria and scoring
   - Award justification

2. All sole-source contracts and emergency procurements, including:
   - Justification for non-competitive bidding
   - Urgency declarations
   - Market research conducted
   - Price reasonableness assessments

3. All contract amendments and extensions, including:
   - Original contract value vs. final value
   - Justification for amendments
   - Approval documentation
   - Performance evaluations

4. All procurement-related communications with:
   - Ministerial offices
   - Political staff
   - External lobbyists
   - Potential contractors

This request relates to understanding how government procurement decisions are made and who benefits from public spending.

### Template 3: Treasury Board - Spending Approvals

**Subject:** Access to Information Request — Treasury Board Spending Approvals and Policy Implementation

To: ATIP Coordinator, Treasury Board Secretariat

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All Treasury Board submissions for new spending programs from January 1, 2015 to present, including:
   - Program descriptions and objectives
   - Cost-benefit analyses
   - Implementation plans
   - Risk assessments

2. All approvals for major procurement projects, including:
   - Business cases
   - Alternative analysis
   - Risk assessments
   - Value for money determinations

3. All policy implementation decisions, including:
   - Regulatory Impact Analysis Statements
   - Stakeholder consultations
   - Economic impact assessments
   - Distributional analyses

4. All communications regarding spending priorities with:
   - Ministerial offices
   - Department officials
   - External stakeholders
   - Provincial/territorial governments

This request relates to understanding how government spending decisions are made and implemented.

### Template 4: Corporate Registries - Family Business Interests

**Subject:** Access to Information Request — Family Business Interests and Investment Portfolios of Government Officials

To: ATIP Coordinator, Innovation, Science and Economic Development Canada

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All corporate registry records for businesses owned or directed by:
   - Current Cabinet ministers and their spouses
   - Senior government officials and their family members
   - Former ministers who left office after January 1, 2015
   - Family members of current and former officials

2. All business registration and incorporation documents including:
   - Company establishment dates and ownership structures
   - Director and officer appointments
   - Shareholder information and capitalization
   - Business activities and sector classifications

3. All investment portfolio and trust information for:
   - Family offices of government officials
   - Blind trust arrangements and compliance
   - Investment fund holdings and management
   - Inter-generational wealth transfer structures

4. All professional and business association memberships for:
   - Government officials and their family members
   - Business partners and associates
   - Advisory board positions and consultancies
   - Lobbying and consulting activities

This request relates to understanding potential conflicts between public duties and private business interests.

### Template 5: Financial Institutions - Investment Portfolio Tracking

**Subject:** Access to Information Request — Investment Portfolios and Financial Holdings of Government Officials

To: ATIP Coordinator, Office of the Superintendent of Financial Institutions

Pursuant to Section 4(1) of the Access to Information Act, I request:

1. All investment portfolio disclosures for government officials, including:
   - Stock and bond holdings
   - Mutual fund and ETF investments
   - Real estate investment trusts
   - Private equity and venture capital holdings

2. All trust and estate planning documents, including:
   - Family trust structures
   - Estate planning arrangements
   - Wealth transfer mechanisms
   - Beneficiary designations

3. All financial account information for:
   - Investment accounts and brokerage services
   - Private banking relationships
   - Wealth management services
   - Family office arrangements

4. All compliance and conflict management records, including:
   - Blind trust establishment and monitoring
   - Conflict of interest assessments
   - Ethics compliance reviews
   - Enforcement actions and remedial measures

This request relates to understanding how government officials manage their financial interests and potential conflicts.

---

## Analysis Framework

### 1. Temporal Pattern Analysis

**Key Patterns to Identify:**
- Asset purchases before policy announcements
- Business establishments before regulatory changes
- Contract awards to newly-formed companies
- Real estate acquisitions before infrastructure announcements

**Analysis Methods:**
- Timeline correlation analysis
- Statistical significance testing
- Network analysis of business relationships
- Geographic analysis of investments

### 2. Value Impact Assessment

**Measurement Framework:**
- Asset appreciation following policy changes
- Contract value vs. market rates
- Business revenue changes after regulatory decisions
- Real estate value increases after zoning changes

**Comparative Analysis:**
- Similar assets in unaffected areas
- Industry benchmarks
- Market performance comparisons
- Historical trend analysis

### 3. Network Centrality Analysis

**Connection Mapping:**
- Business relationship networks
- Political donation patterns
- Lobbying registration overlaps
- Corporate board interlocks

**Centrality Metrics:**
- Degree centrality (number of connections)
- Betweenness centrality (bridge positions)
- Closeness centrality (access to information)
- Eigenvector centrality (influence within network)

---

## Public Interest Framing

### Legitimate Areas of Inquiry

**Accountability Questions:**
- How do government officials ensure policies serve public interest rather than private gain?
- What safeguards exist against policy-for-profit patterns?
- How transparent are decision-making processes?
- What recourse exists when conflicts arise?

**Evidence-Based Messaging:**
- "Understanding policy impacts on official assets"
- "Analyzing procurement patterns for fairness"
- "Tracking business interests of public officials"
- "Ensuring public service serves public interest"

**Avoid:**
- Allegations of illegal activity without evidence
- Speculation about motives
- Personal attacks on individuals
- Conspiracy theories

---

## Success Metrics

### Evidence Collection Success
- ATIP response rate: >80%
- Asset declaration completeness: >90%
- Contract data completeness: >85%
- Network mapping coverage: >75%

### Analysis Quality
- Pattern identification accuracy: Expert validation
- Statistical significance: p < 0.05
- Peer review publication: Academic journals
- Media citation rate: Major outlets

### Public Impact
- Policy discussions referencing findings
- Ethics investigations initiated
- Legislative changes proposed
- Citizen engagement increased

---

## Risk Mitigation

### Legal Risks
- **Risk:** Defamation allegations
- **Mitigation:** Stick to documented facts, qualified language

### Privacy Risks
- **Risk:** Privacy law violations
- **Mitigation:** Focus on public officials, use public records

### Political Risks
- **Risk:** Political backlash
- **Mitigation:** Evidence-based approach, bipartisan framing

### Technical Risks
- **Risk:** Data analysis errors
- **Mitigation:** Peer review, methodology transparency

---

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- File priority ATIP requests for asset declarations
- Set up contract tracking database
- Create network analysis framework

### Phase 2: Data Collection (Week 3-6)
- Process received asset declarations
- Collect contract award data
- Map business relationship networks

### Phase 3: Analysis (Week 7-10)
- Conduct temporal pattern analysis
- Perform value impact assessments
- Complete network centrality analysis

### Phase 4: Public Engagement (Week 11-12)
- Release evidence-based findings
- Engage media and policymakers
- Support citizen advocacy efforts

---

## Conclusion

The Government Wealth Tracking Framework extends Veritas accountability tools to examine how public officials might benefit from policy decisions. By focusing on documented evidence, temporal patterns, and verifiable data, this framework provides citizens with tools to understand potential conflicts between public service and private enrichment.

This approach maintains the Veritas commitment to evidence-based accountability while addressing legitimate public interest questions about the intersection of policy-making and personal wealth.

---

*Document prepared for Veritas government wealth tracking integration.*
*Updated: June 26, 2026*
