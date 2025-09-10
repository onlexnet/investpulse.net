# ARCHITECTURE

## Overview
The Predictive Trading Python App is a modular, event-driven system that monitors JSON files containing ticker symbols, downloads SEC EDGAR filings, extracts financial facts, and stores them in Parquet format for analysis.

## System Architecture

### High-Level Flow
```
JSON File → File Watcher → SEC EDGAR Download → Fact Extraction → Parquet Storage
     ↓             ↓              ↓                    ↓              ↓
  input/       File Monitor    sec-edgar-filings/   Processing     output/
```

## Core Components

### 1. File Watcher (`src/file_watcher.py`)
**Purpose**: Monitors the `input/` directory for new JSON files containing ticker symbols.

**Key Classes**:
- `TickerFileHandler`: Extends `FileSystemEventHandler` to handle file creation events
- Parses JSON files to extract ticker symbols
- Triggers processing workflow via callback mechanism

**Dependencies**: `watchdog`, `json`, `logging`

**Flow**:
1. Observer monitors `input/` directory
2. On file creation, validates JSON structure
3. Extracts ticker symbol from JSON
4. Invokes callback with ticker for downstream processing

### 2. SEC EDGAR Downloader (`src/sec_edgar_downloader.py`)
**Purpose**: Downloads real SEC filings (10-Q, 10-K) from EDGAR database.

**Key Functions**:
- `download_sec_filings()`: Downloads filings using `sec-edgar-downloader` library
- Navigates complex directory structure created by downloader
- Returns path to actual filing file (HTML/TXT)

**Dependencies**: `sec-edgar-downloader`, `os`

**Storage Structure**:
```
sec-edgar-filings/
└── {TICKER}/
    └── {FORM_TYPE}/
        └── {ACCESSION_NUMBER}/
            ├── full-submission.txt
            ├── primary-document.html
            └── ...
```

### 3. Fact Extractor (`src/fact_extractor.py`)
**Purpose**: Parses SEC filing documents and extracts top 10 investment-relevant facts.

**Key Functions**:
- `extract_top_facts()`: Uses BeautifulSoup to parse HTML/TXT filings
- `save_facts_to_parquet()`: Converts facts to DataFrame and saves as Parquet

**Extraction Strategy**:
1. Parse HTML tables for structured financial data
2. Fallback to text lines containing financial indicators ($, %)
3. Returns exactly 10 facts in standardized format

**Dependencies**: `beautifulsoup4`, `pandas`, `pyarrow`

### 4. Logger (`src/logger.py`)
**Purpose**: Centralized logging configuration for application monitoring.

**Features**:
- File-based logging with timestamps
- Prevents duplicate handlers
- Configurable log levels
- Tracks processing workflow and errors

### 5. Main Application (`src/app.py`)
**Purpose**: Orchestrates the entire workflow and provides entry point.

**Key Functions**:
- `process_ticker()`: Main processing pipeline for each ticker
- Coordinates all components in sequence
- Handles errors and logging

**Workflow**:
1. Setup logging
2. Initialize file watcher
3. For each ticker: Download → Extract → Save
4. Log all operations and errors

## Data Flow Architecture

### Input Layer
- **Format**: JSON files in `input/` directory
- **Schema**: `{"ticker": "SYMBOL"}`
- **Trigger**: File system events (creation)

### Processing Layer
- **Download**: SEC EDGAR API integration
- **Parse**: HTML/TXT document processing
- **Extract**: Financial fact identification and ranking
- **Transform**: Structured data conversion

### Storage Layer
- **Format**: Parquet files in `output/` directory
- **Schema**: `{fact: string, value: string}`
- **Naming**: `{TICKER}_facts.parquet`

### Analysis Layer
- **Tool**: Jupyter notebook with PySpark
- **Purpose**: Interactive analysis of extracted facts
- **Features**: Schema exploration, aggregation, visualization

## Technology Stack

### Core Libraries
- **File Monitoring**: `watchdog`
- **SEC Data**: `sec-edgar-downloader`
- **HTML Parsing**: `beautifulsoup4`
- **Data Processing**: `pandas`
- **Storage**: `pyarrow` (Parquet)
- **Analysis**: `pyspark`

### Development Tools
- **Testing**: `pytest`
- **Type Hints**: `typing`
- **Logging**: Built-in `logging`

## Directory Structure
```
backend/
├── src/
│   ├── app.py              # Main orchestrator
│   ├── file_watcher.py     # File system monitoring
│   ├── sec_edgar_downloader.py  # SEC data fetching
│   ├── fact_extractor.py   # Document parsing
│   └── logger.py           # Logging utilities
├── tests/
│   ├── test_app.py         # Integration tests
│   ├── test_file_watcher.py # File monitoring tests
│   ├── test_sec_edgar_downloader.py # Download tests
│   └── test_fact_extractor.py # Extraction tests
├── input/                  # Ticker JSON files (monitored)
├── output/                 # Parquet results
├── sec-edgar-filings/      # Downloaded SEC filings
├── analyze_parquet_pyspark.ipynb # Analysis notebook
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Scalability Considerations

### Current Limitations
- Single-threaded file processing
- Local file system storage
- Memory-based fact extraction

### Potential Enhancements
- **Concurrency**: Multi-threaded ticker processing
- **Storage**: Cloud storage integration (S3, Azure Blob)
- **Streaming**: Real-time processing with message queues
- **Caching**: Redis for downloaded filings
- **API**: REST API for programmatic access

## Error Handling Strategy

### File Watcher
- Invalid JSON format handling
- Missing ticker field validation
- File access permission errors

### SEC Downloader
- Network connectivity issues
- Rate limiting compliance
- Missing filing handling

### Fact Extractor
- Malformed HTML/TXT parsing
- Insufficient fact extraction fallbacks
- Encoding error handling

### Storage
- Disk space validation
- File permission checks
- Parquet serialization errors

## Security Considerations

### Data Privacy
- SEC filings are public data
- No sensitive information processing
- Local storage only

### External Dependencies
- SEC EDGAR API rate limiting compliance
- Email address requirement for SEC requests
- Network security for external API calls

## Monitoring and Observability

### Logging Strategy
- Application-level logging to `app.log`
- Structured log format with timestamps
- Error tracking and debugging information

### Metrics
- Processing time per ticker
- Success/failure rates
- File system utilization

### Health Checks
- Directory accessibility
- External API availability
- Disk space monitoring

## Deployment Architecture

### Local Development
- Python virtual environment
- File-based configuration
- Interactive Jupyter analysis

### Production Considerations
- Containerization with Docker
- Environment variable configuration
- Persistent volume for data storage
- Monitoring and alerting integration

## API Integration

### SEC EDGAR API
- **Endpoint**: Official SEC EDGAR database
- **Authentication**: Email address requirement
- **Rate Limits**: Respectful request timing
- **Data Format**: HTML, TXT, XML filings

### Future APIs
- Financial data providers (Alpha Vantage, Yahoo Finance)
- News sentiment analysis
- Market data integration
