---
post_title: "InvestPulse.net Architecture Overview"
author1: "Development Team"
post_slug: "architecture-overview"
microsoft_alias: "investpulse-dev"
featured_image: ""
categories: ["Architecture", "Documentation"]
tags: ["monorepo", "nextjs", "azure", "terraform", "python", "financial-data"]
ai_note: "AI assisted in documentation creation"
summary: "Comprehensive architecture overview of the InvestPulse.net monorepo including frontend, backend, and infrastructure components"
post_date: "2025-09-10"
---

## Architecture Overview

InvestPulse.net is a financial dashboard application built as a monorepo with clear separation of concerns across frontend, backend, and infrastructure layers. The architecture follows modern cloud-native patterns with Azure as the primary cloud provider and Python-based financial data processing.

## Monorepo Structure

```
/investpulse.net/
├── webapp/           # Next.js 15 Frontend Application
├── backend/          # Python Data Processing Application
├── try/             # Backend Services & APIs (Microservices) [AI-ignored]
├── infra/           # Infrastructure as Code (Terraform)
├── docs/            # Project Documentation
├── scripts/         # Automation Scripts
├── tests/           # Global Test Suites
└── webapi/          # Web API Layer
```

## Frontend Layer (/webapp)

### Technology Stack
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript (strictly typed)
- **Styling**: Tailwind CSS + shadcn/ui components
- **Icons**: Lucide React
- **Fonts**: Next.js font optimization

### Architecture Principles
- **Local Data Only**: No backend integration in webapp package
- **Component-Based**: Modular UI components with shadcn/ui
- **Type Safety**: Comprehensive TypeScript interfaces
- **Path Aliases**: Clean imports using `@/components`, `@/lib` patterns
- **No Global State**: Local component state management

### Key Components
- **Entry Point**: `src/app/page.tsx` (renders PopularStocksRanking)
- **UI Primitives**: `src/components/ui/` (Card, Badge, Table, etc.)
- **Business Logic**: `src/components/PopularStocksRanking.tsx`
- **Utilities**: `src/lib/utils.ts`

### Development Workflow
```bash
# Development server (custom port)
npm run dev -- -p 8080

# Production build
npm run build && npm start

# Code quality
npm run lint
```

## Backend Layer (/backend)

### Technology Stack
- **Language**: Python 3.11+
- **Data Processing**: pandas, pyarrow (Parquet format)
- **Web Scraping**: BeautifulSoup4, requests
- **Financial Data**: sec-edgar-downloader
- **File Monitoring**: watchdog
- **Analytics**: PySpark (optional)

### Architecture Pattern
- **Event-Driven**: File system watcher triggers processing pipeline
- **ETL Pipeline**: Extract → Transform → Load financial data
- **Modular Components**: Separate modules for each processing stage
- **Data Lake Pattern**: Raw and processed data storage

### Core Components

#### File Watcher (`src/file_watcher.py`)
- Monitors `input/` folder for JSON ticker files
- Triggers processing pipeline on file creation
- Uses watchdog library for cross-platform file system events

#### SEC Data Downloader (`src/sec_edgar_downloader.py`)
- Downloads SEC EDGAR filings (10-K, 10-Q forms)
- Integrates with sec-edgar-downloader library
- Handles rate limiting and error recovery
- Stores raw filings in `sec-edgar-filings/` directory

#### Fact Extractor (`src/fact_extractor.py`)
- Parses SEC filing HTML/TXT content
- Extracts top 10 financial facts using BeautifulSoup
- Identifies key metrics (revenue, income, ratios)
- Structures data for investment decision making

#### Data Storage
- **Input Format**: JSON files with ticker symbols
- **Processing Format**: Raw SEC filing documents
- **Output Format**: Parquet files with extracted facts
- **Directory Structure**:
  ```
  backend/
  ├── input/           # JSON ticker files
  ├── output/          # Processed Parquet files
  └── sec-edgar-filings/ # Raw SEC documents
  ```

### Processing Pipeline
```
JSON Ticker → SEC Download → Fact Extraction → Parquet Storage
     ↓              ↓              ↓              ↓
  File Watch    Raw Filings   Financial Facts   Data Lake
```

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.app

# Run tests
pytest tests/

# Add ticker for processing
echo '{"ticker": "AAPL"}' > input/aapl.json
```

## Backend Services Layer (/try)

### Architecture Note
- **Microservices Architecture**: Distributed services pattern
- **API-First Design**: RESTful APIs and service contracts
- **Shared Libraries**: Common utilities and interfaces
- **Service Isolation**: Independent deployable units

**Note**: Backend code in `/try` is managed independently and not modified by AI agents per project conventions.

## Infrastructure Layer (/infra)

### Technology Stack
- **IaC Tool**: Terraform 1.10+
- **Cloud Provider**: Microsoft Azure
- **CI/CD**: GitHub Actions
- **DNS Management**: Cloudflare
- **State Management**: Terraform Cloud

### Key Infrastructure Components

#### Core Resources (`main.tf`)
- **Azure Static Web Apps**: Frontend hosting with CDN
- **Resource Groups**: Environment-based organization
- **Custom Domains**: Environment-specific DNS routing
- **GitHub Environments**: Deployment target configuration

#### Configuration Management
- **Variables**: Defined in `variables.tf`
- **Outputs**: Resource endpoints in `outputs.tf`
- **Environment Configuration**: `terraform.tfvars`
- **Secrets**: `secret.auto.tfvars` (git-ignored)

#### Cost Optimization
- **Free Tier Usage**: Azure Static Web Apps (Free)
- **Bandwidth Limits**: 0.5 GB/month monitoring
- **Domain Limits**: Up to 2 custom domains
- **No API/Functions**: Keeps costs at $0/month

### Environment Strategy
```
Production:     investpulse.net
Development:    dev.investpulse.net
Staging:        staging.investpulse.net
```

## Deployment Architecture

### CI/CD Pipeline
```yaml
# GitHub Actions Workflow
Frontend Deployment:
├── Build Next.js Application
├── Run Tests & Linting
├── Deploy to Azure Static Web Apps
└── Verify Deployment

Backend Processing:
├── Python Environment Setup
├── Run Unit Tests
├── Package Dependencies
└── Deploy Processing Logic

Infrastructure:
├── Terraform Plan
├── Security Validation
├── Terraform Apply
└── Resource Verification
```

### Deployment Triggers
- **Frontend**: Changes in `webapp/**` → Azure Static Web Apps
- **Backend**: Manual deployment or scheduled processing
- **Infrastructure**: Changes in `infra/**` → Terraform Cloud

## Data Flow Architecture

### Frontend Data Flow
```
Static Data → React Components → User Interface → Local State
```

### Backend Data Flow
```
JSON Input → File Watcher → SEC Download → Fact Extraction → Parquet Output
     ↓            ↓             ↓              ↓              ↓
Ticker Files  Event Handler  Raw Filings  Structured Data  Data Lake
```

### Infrastructure Data Flow
```
GitHub → Actions → Terraform Cloud → Azure Resources → DNS
```

## Security Architecture

### Data Protection
- **In Transit**: TLS 1.3 encryption for all communications
- **At Rest**: Azure Storage encryption for static files
- **Secrets**: Terraform Cloud secure variable storage
- **API Keys**: Environment-specific secret management

### Access Control
- **Frontend**: Static hosting with security headers
- **Backend**: File system permissions and logging
- **Infrastructure**: Terraform Cloud RBAC

## Monitoring & Observability

### Application Monitoring
- **Frontend**: Azure Static Web Apps analytics
- **Backend**: Python logging with structured output
- **Infrastructure**: Terraform state monitoring

### Logging Strategy
- **Python Logging**: Centralized logging to `app.log`
- **File Processing**: Event-driven logging for each ticker
- **Error Handling**: Comprehensive exception logging

## Scalability & Performance

### Frontend Optimization
- **Static Generation**: Next.js SSG for optimal performance
- **CDN Distribution**: Global edge locations via Azure
- **Component Optimization**: Lazy loading and code splitting

### Backend Scalability
- **File Processing**: Asynchronous processing pipeline
- **Data Storage**: Parquet format for analytical workloads
- **Resource Management**: Configurable processing limits

### Infrastructure Scalability
- **Environment Isolation**: Independent resource groups
- **DNS Management**: Cloudflare for global distribution
- **Cost Controls**: Free tier utilization with monitoring

## Development Conventions

### Code Quality
- **TypeScript**: Strict mode for frontend
- **Python**: Type hints and docstrings
- **Testing**: Unit tests for all core components
- **Linting**: ESLint for frontend, pytest for backend

### Documentation Standards
- **Architecture**: Documented in this file
- **Components**: Individual README files
- **Development Plans**: Feature-specific planning docs

## Integration Points

### External Dependencies
- **SEC EDGAR API**: Financial data source
- **Azure Static Web Apps**: Frontend hosting
- **Cloudflare DNS**: Domain management
- **GitHub Actions**: CI/CD automation

### Internal Dependencies
- **Shared Data**: Parquet files between backend and potential APIs
- **Configuration**: Environment-specific settings
- **Monitoring**: Cross-layer observability

## Future Architecture Considerations

### Planned Enhancements
- **Real-time Processing**: WebSocket integration for live data
- **API Integration**: Connect frontend to processed data
- **Advanced Analytics**: Machine learning integration
- **Multi-tenant**: Support for multiple users/portfolios

### Scalability Roadmap
- **Containerization**: Docker adoption for backend services
- **Event Streaming**: Kafka/Azure Event Hubs for real-time data
- **Data Warehouse**: Azure Synapse for large-scale analytics
- **Global Distribution**: Multi-region deployment strategy