# GPT-5.5 Implementation Guide: Evidence Visualization Dashboard

## Project Context

**Project:** TAKE_CANADA_BACK - Evidence archive documenting Canadian government corruption  
**Current State:** Basic React frontend with evidence vault, FastAPI backend  
**Goal:** Transform into three-tier visualization dashboard (Executive → Deep-Dive → Source Vault)

## Data Preparation Status ✅

### Completed
- ✅ Data extraction script: `scripts/extract_visualization_data.py`
- ✅ Timeline events extracted: 24 events (2013-2020 platform funding, simulations, activation)
- ✅ Network nodes extracted: 35 entities (pharma, government, foundations, individuals)
- ✅ Financial flows extracted: 3 flows (DARPA→Moderna, Gates→Moderna, etc.)
- ✅ Lobbying meetings extracted: 9 meetings (Innovative Medicines Canada)
- ✅ Backend API endpoints: `/api/visualization/*` (timeline, network, financial-flow, lobbying, vaccine-waste, revolving-door)
- ✅ Frontend libraries installed: d3, reactflow, recharts, mermaid, framer-motion, zustand

### Data Files Location
```
frontend/src/data/
├── visualization_data.json (combined)
├── timeline_events.json
├── network_nodes.json
├── financial_flows.json
└── lobbying_meetings.json
```

### API Endpoints
```
GET /api/visualization/timeline - Timeline events
GET /api/visualization/network - Network graph (nodes + edges)
GET /api/visualization/financial-flow - Financial flows
GET /api/visualization/lobbying - Lobbying meetings
GET /api/visualization/vaccine-waste - Vaccine waste data
GET /api/visualization/revolving-door - Revolving door personnel
GET /api/visualization/all - All data combined
```

## Current Frontend Structure

### Existing Components
```
frontend/src/
├── App.jsx (main app, vault view)
├── api.js (API client)
├── components/
│   ├── AdminView.jsx
│   ├── AnalysisView.jsx
│   ├── EconomicEvidenceDashboard.tsx
│   ├── EntitiesView.jsx
│   ├── EvidenceDetail.jsx
│   ├── IngestForm.jsx
│   ├── LoginModal.jsx
│   ├── RelationshipsView.jsx
│   ├── TimelineView.jsx
│   └── [other components]
└── lib/
    └── format.js
```

### New Components Created (Starter)
```
frontend/src/views/Dashboard/
├── HeroTimeline.jsx (smoking gun timeline)
├── MoneyFlowSankey.jsx (financial flow visualization)
└── VaccineWasteChart.jsx (waste bar chart)
```

## Implementation Request for GPT-5.5

### Phase 1: Executive Dashboard (Tier 1)

**Request:** Create the executive dashboard landing page with hero visualizations

**Requirements:**
1. Create `frontend/src/views/Dashboard/index.jsx` - Main dashboard component
2. Implement 2x2 grid layout with:
   - Top-left: HeroTimeline (already created, integrate)
   - Bottom-left: MoneyFlowSankey (already created, integrate)
   - Top-right: VaccineWasteChart (already created, integrate)
   - Bottom-right: LobbyingHeatmap (create new)
3. Add header with Merkle root display
4. Add navigation to deep-dive modules
5. Make responsive (desktop/tablet/mobile)

**Data Sources:**
- Timeline: `/api/visualization/timeline`
- Financial: `/api/visualization/financial-flow`
- Vaccine waste: `/api/visualization/vaccine-waste`
- Lobbying: `/api/visualization/lobbying`

**Styling:**
- Use Tailwind CSS
- Dark theme (slate-900 to slate-800 gradients)
- Use framer-motion for animations
- Ensure WCAG 2.1 AA compliance

---

### Phase 2: Deep-Dive Modules (Tier 2)

**Request:** Create Module 1: Pre-Pandemic Platform Explorer

**Requirements:**
1. Create `frontend/src/views/Modules/PlatformExplorer/index.jsx`
2. Implement expanded timeline with:
   - Drag-to-zoom time range
   - Parallel tracks (Funding, Patents, Simulations, Personnel)
   - Source document popovers
   - "What if" scenarios (toggle layers)
3. Implement funding network graph using ReactFlow:
   - Nodes: Funding sources, recipients, intermediaries
   - Edges: Money flows with amounts
   - Layer toggle (DARPA, Gates, NIH, Private)
   - Aggregate view (total per entity)
4. Add source document links
5. Export functionality (PDF, CSV, PNG)

**Data Sources:**
- Timeline: `/api/visualization/timeline`
- Network: `/api/visualization/network`
- Financial: `/api/visualization/financial-flow`

**Libraries:**
- ReactFlow for network graph
- D3.js for timeline zooming
- Recharts for aggregate charts

---

### Phase 3: Source Vault (Tier 3)

**Request:** Create source vault with document reader

**Requirements:**
1. Create `frontend/src/views/SourceVault/index.jsx`
2. Implement document grid view:
   - Thumbnail previews
   - Metadata cards (source, date, classification)
   - Citation count badge
   - Cross-reference indicators
3. Implement document reader:
   - Split screen (document + evidence context)
   - Auto-highlight evidence passages
   - Sidebar with related documents
   - Annotation support
4. Add search and filter
5. Export citation bundles

**Data Sources:**
- Use existing `/api/evidence/*` endpoints
- Cross-reference with visualization data

---

## Integration Instructions

### Step 1: Update App.jsx
Add new navigation structure:
```jsx
// Add to App.jsx state
const [activeView, setActiveView] = useState('dashboard'); // 'dashboard', 'modules', 'vault'

// Add navigation component
<Navigation activeView={activeView} setActiveView={setActiveView} />

// Conditional rendering
{activeView === 'dashboard' && <Dashboard />}
{activeView === 'modules' && <Modules />}
{activeView === 'vault' && <SourceVault />}
{activeView === 'vault' && <EvidenceVault />}
```

### Step 2: Create Navigation Component
```jsx
// frontend/src/components/Navigation.jsx
// Three-tier navigation
// - Executive Dashboard
// - Deep-Dive Modules (list of 6 modules)
// - Source Vault
```

### Step 3: Add State Management
```jsx
// frontend/src/store/useVisualizationStore.js
// Using Zustand
// - Timeline filters
// - Network layer toggles
// - Selected evidence
// - Export settings
```

---

## Design Specification Reference

See the full design specification document for:
- Component architecture details
- User experience flows
- Accessibility requirements
- Mobile responsiveness
- Internationalization support
- Security considerations

---

## Testing Requirements

1. **Unit Tests:** Test each visualization component
2. **Integration Tests:** Test API integration
3. **E2E Tests:** Test user flows (using Playwright if available)
4. **Accessibility:** Test with screen readers
5. **Performance:** Test with large datasets

---

## Success Metrics

- Page load time: <2 seconds
- Time to interactive: <3 seconds
- Lighthouse score: >90
- Module completion rate: >60%
- Export rate: >20%

---

## Next Steps After Implementation

1. Phase 2: Implement remaining 5 deep-dive modules
2. Phase 3: Implement source vault
3. Phase 4: Polish and optimization
4. Phase 5: Advanced features (AI discovery, real-time collaboration)

---

## File Structure After Implementation

```
frontend/src/
├── views/
│   ├── Dashboard/
│   │   ├── index.jsx (main dashboard)
│   │   ├── HeroTimeline.jsx
│   │   ├── MoneyFlowSankey.jsx
│   │   ├── VaccineWasteChart.jsx
│   │   └── LobbyingHeatmap.jsx
│   ├── Modules/
│   │   ├── PlatformExplorer/
│   │   ├── ContractAnalyzer/
│   │   ├── RevolvingDoorTracker/
│   │   ├── PoliticalMoneyTrail/
│   │   ├── FamilyNetworkInvestigator/
│   │   └── LobbyingIntelligence/
│   └── SourceVault/
│       ├── index.jsx
│       ├── DocumentGrid.jsx
│       └── DocumentReader.jsx
├── components/
│   ├── visualizations/
│   │   ├── TimelineChart.jsx
│   │   ├── NetworkGraph.jsx
│   │   ├── SankeyDiagram.jsx
│   │   └── Heatmap.jsx
│   └── shared/
│       ├── Navigation.jsx
│       └── Header.jsx
├── store/
│   └── useVisualizationStore.js
└── lib/
    ├── data-transformers.js
    └── visualization-utils.js
```

---

## Important Notes

1. **Data is already extracted** - No need to parse markdown files
2. **API endpoints are ready** - Just fetch from `/api/visualization/*`
3. **Libraries are installed** - d3, reactflow, recharts, mermaid, framer-motion, zustand
4. **Starter components exist** - HeroTimeline, MoneyFlowSankey, VaccineWasteChart
5. **Focus on integration** - Connect components, add navigation, implement state management

---

## Code Style

- Use functional components with hooks
- Use TypeScript for new components (optional but recommended)
- Follow existing code style in the project
- Add comments for complex logic
- Use Tailwind CSS for styling
- Use framer-motion for animations

---

## Questions for GPT-5.5

If clarification needed:
1. Should the dashboard replace the current vault view or be an additional view?
2. Should we maintain backward compatibility with existing components?
3. What should be the default view when users first visit?
4. Should we implement lazy loading for modules?

---

## Implementation Priority

1. **HIGH:** Executive Dashboard (Phase 1) - Landing page with hero visualizations
2. **HIGH:** Module 1: Platform Explorer (Phase 2) - First deep-dive module
3. **MEDIUM:** Navigation and routing (Phase 1-2 integration)
4. **MEDIUM:** State management setup (Zustand store)
5. **LOW:** Source vault (Phase 3) - Can be implemented later

---

## Contact

If issues arise during implementation:
- Check API endpoints are accessible: `curl http://localhost:8000/api/visualization/timeline`
- Check data files exist: `ls frontend/src/data/`
- Check libraries installed: `cat frontend/package.json`
- Refer to existing components for patterns: `frontend/src/components/`
