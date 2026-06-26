# Veritas Project Structure

## Overview
Veritas is an open-source evidentiary collection engine for documenting government accountability with cryptographic integrity guarantees.

## Architecture

### Backend (`/backend`)
FastAPI-based REST API with PostgreSQL RLS for tamper-evidence.

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and initialization
│   ├── models.py              # All database models (unified)
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── auth.py                # JWT authentication
│   ├── storage.py             # File storage management
│   ├── signed_export.py       # Ed25519 cryptographic signing
│   ├── warc.py                # WARC 1.1 archive format
│   ├── custody.py             # Chain of custody management
│   └── routers/               # API endpoints
│       ├── __init__.py
│       ├── evidence.py        # Evidence collection
│       ├── entities.py        # Entity management
│       ├── relationships.py   # Relationship tracking
│       ├── timeline.py        # Timeline events
│       ├── collect.py         # Evidence collection tools
│       ├── seal.py            # Digital sealing
│       ├── export.py          # Export functionality
│       ├── auth.py            # Authentication endpoints
│       ├── economic.py        # Economic evidence tracking
│       ├── wealth_gap.py     # Wealth gap analysis
│       ├── historical_parallels.py # Historical comparisons
│       └── transparency.py    # Transparency campaign
├── scripts/
│   └── collect_economic_evidence.py # Evidence collection script
├── Dockerfile                 # Container configuration
└── requirements.txt           # Python dependencies
```

### Frontend (`/frontend`)
React-based web interface for evidence visualization and collection.

```
frontend/
├── src/
│   ├── components/
│   │   └── EconomicEvidenceDashboard.tsx # Main dashboard
│   └── ... (other React components)
├── package.json
└── vercel.json               # Vercel deployment configuration
```

### Documentation (`/docs`)
Comprehensive documentation for the project.

```
docs/
├── README.md                 # Project overview
├── API.md                    # API documentation
├── ARCHITECTURE.md           # System architecture
├── INTEGRITY.md              # Data integrity guarantees
├── SECURITY.md               # Security considerations
├── ROADMAP.md                # Development roadmap
├── USAGE.md                  # Usage instructions
├── GLOSSARY.md               # Terminology
├── PEER_MODE.md              # Peer operating framework
├── PUBLIC_DATA_RELEASE.md    # Data release procedures
├── TRANSPARENCY_CAMPAIGN.md  # Government accountability campaign
└── PROJECT_STRUCTURE.md       # This file
```

## Core Features

### 1. Evidence Collection
- Cryptographic hash-chained custody log
- File integrity verification
- Metadata extraction and indexing
- Screenshot capture with Playwright
- HTTP header preservation

### 2. Economic Evidence System
- Small business destruction tracking
- Wealth gap policy impact analysis
- Government hypocrisy documentation
- Inflation tax evidence collection
- Historical parallels to authoritarian regimes

### 3. Transparency Campaign
Four accountability tracks:
- **Emergency Powers** - Emergencies Act 2022, interim orders, Charter suspensions
- **Surveillance Infrastructure** - CSE, FINTRAC, Bills C-22/C-26 data collection
- **Financial Transparency** - Bank of Canada operations, QE, banking concentration
- **Civil Liberties Litigation** - CCLA, BCCLA, Citizen Lab challenges

### 4. Export Capabilities
- Signed export bundles with Ed25519 verification
- WARC 1.1 format for archival interoperability
- Cryptographic timestamps (RFC3161)
- Manifest generation with integrity proofs

### 5. Security & Integrity
- PostgreSQL Row-Level Security (RLS) for append-only logs
- JWT authentication for write operations
- Cryptographic evidence chain of custody
- Tamper-evident storage with hash chaining

## API Endpoints

### Core Evidence
- `/api/evidence` - Evidence CRUD operations
- `/api/entities` - Entity management
- `/api/relationships` - Relationship tracking
- `/api/timeline` - Timeline events

### Economic Evidence
- `/api/economic/*` - Economic indicators and business metrics
- `/api/wealth-gap/*` - Wealth gap analysis and policy impacts
- `/api/historical-parallels/*` - Historical regime comparisons
- `/api/transparency/*` - Transparency campaign data

### Export & Verification
- `/api/export/manifest` - Generate vault manifest
- `/api/export/package` - Create export packages
- `/api/export/warc` - WARC format export
- `/api/export/signed` - Cryptographically signed bundles
- `/api/export/pubkey` - Ed25519 public key for verification

## Deployment

### Backend (Railway)
- **URL**: https://backend-production-cf1f.up.railway.app
- **Database**: PostgreSQL with RLS policies
- **Storage**: Persistent volume for evidence files
- **Authentication**: JWT-based

### Frontend (Vercel)
- **URL**: https://proofstacked.com
- **API Proxy**: Routes `/api/*` to Railway backend
- **Environment**: Production with API base URL configuration

## Security Model

### Data Integrity
- SHA-256 hashing for all evidence files
- Hash-chained custody log prevents tampering
- PostgreSQL RLS ensures append-only operations
- Cryptographic signatures for export verification

### Access Control
- JWT tokens for authenticated operations
- Public read access for evidence metadata
- Write operations require authentication
- Role-based access control (admin-only for sensitive operations)

### Audit Trail
- Complete chain of custody for all evidence
- Timestamped access logs
- Cryptographic verification of data integrity
- Export bundles with verifiable signatures

## Development Status

### Completed Features ✅
- Core evidence collection and storage
- Cryptographic integrity guarantees
- Economic evidence tracking system
- Historical parallels analysis
- Transparency campaign data collection
- Railway deployment with all APIs
- Frontend dashboard interface
- WARC export format
- Signed export bundles
- PostgreSQL RLS implementation

### Pending Features 🔄
- Multi-user roles beyond single admin
- Advanced search and filtering
- Real-time notifications
- Mobile-responsive interface
- Automated evidence collection pipelines

## Data Model

### Evidence
```typescript
interface Evidence {
  id: number;
  sha256: string;
  title: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  source_url?: string;
  captured_at?: Date;
  collected_by?: string;
  created_at: Date;
}
```

### Economic Indicators
```typescript
interface EconomicIndicator {
  id: number;
  date: Date;
  indicator_type: string;
  value: number;
  source: string;
  region: string;
}
```

### Policy Actions
```typescript
interface PolicyAction {
  id: number;
  date: Date;
  policy_type: string;
  policy_name: string;
  description: string;
  claimed_purpose: string;
  actual_impact: string;
  affected_groups: string;
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with cryptographic integrity in mind
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open-source and available under the MIT License.

## Support

For technical support or questions about the evidence collection system:
- Review the API documentation
- Check the integrity guarantees
- Consult the security considerations
- Examine the usage instructions
