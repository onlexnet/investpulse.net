# ARCHITECTURE

## Overview
The Predictive Trading Python App is a modular, event-driven system that monitors JSON files containing ticker symbols, downloads SEC EDGAR filings, extracts financial facts, and stores them in Parquet format for analysis.

## System Architecture

### High-Level Flow
```
JSON File → File Watcher → Processing State → SEC EDGAR Download → Fact Extraction → Parquet Storage
     ↓             ↓              ↓                    ↓                    ↓              ↓
  input/    File Monitor   input/processing/   sec-edgar-filings/     Processing      output/
            + State Mgmt    + State Files
```

## Core Components

### 1. File Watcher (`src/file_watcher.py`)
**Purpose**: Monitors the `input/` directory for new JSON files containing ticker symbols.

**Key Classes**:
- `TickerFileHandler`: Extends `FileSystemEventHandler` to handle file creation events
- Parses JSON files to extract ticker symbols
- **NEW**: Moves files to `input/processing/` directory for organized workflow
- **NEW**: Creates ProcessingState tracking for each ticker file
- **NEW**: Generates state files (`ticker-name.state.json`) to track processing progress
- Triggers processing workflow via callback mechanism with ProcessingState object

**Dependencies**: `watchdog`, `json`, `logging`, `shutil`, `ProcessingState`

**Flow**:
1. Observer monitors `input/` directory
2. On file creation, validates JSON structure
3. Extracts ticker symbol from JSON
4. **NEW**: Moves file to `input/processing/` directory
5. **NEW**: Creates ProcessingState object with initial status
6. **NEW**: Saves state file in processing directory
7. Invokes callback with ProcessingState for downstream processing

**File Management**:
- Original files: `input/{ticker}.json`
- Moved to: `input/processing/{ticker}.json`
- State files: `input/processing/{ticker}.state.json`

### 2. Processing State Management (`src/processing_state.py`)
**Purpose**: Manages the complete lifecycle state of ticker file processing from discovery to completion.

**Key Classes**:
- `ProcessingStatus`: Enum defining all processing stages
- `ProcessingState`: Dataclass tracking complete processing context

**Processing Stages**:
1. `DISCOVERED`: File detected in input directory
2. `MOVED_TO_PROCESSING`: File moved to processing directory
3. `DOWNLOADING_SEC_FILING`: SEC filing download in progress
4. `SEC_FILING_DOWNLOADED`: SEC filing successfully downloaded
5. `EXTRACTING_FACTS`: Fact extraction in progress
6. `FACTS_EXTRACTED`: Facts successfully extracted
7. `SAVING_PARQUET`: Parquet file creation in progress
8. `COMPLETED`: Processing successfully completed
9. `ERROR`: Processing failed with error

**State Tracking Features**:
- Timestamps for creation and updates
- File path tracking (original, processing, state, SEC filing, parquet output)
- Error message capture
- Metadata storage for additional context
- JSON serialization/deserialization
- Persistent state file management

**Dependencies**: `dataclasses`, `datetime`, `enum`, `json`, `os`

**Usage Pattern**:
```python
# Create initial state
state = ProcessingState(ticker="AAPL", original_file_path="input/aapl.json")

# Update status throughout processing
state.update_status(ProcessingStatus.DOWNLOADING_SEC_FILING)
state.set_sec_filing_path("/path/to/filing.txt")
state.set_parquet_output_path("/path/to/output.parquet")

# Persist state
state.save_to_file()
```

### 3. SEC EDGAR Downloader (`src/sec_edgar_downloader.py`)
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

### 4. Fact Extractor (`src/fact_extractor.py`)
**Purpose**: Parses SEC filing documents and extracts top 10 investment-relevant facts.

**Key Functions**:
- `extract_top_facts()`: Uses BeautifulSoup to parse HTML/TXT filings
- `save_facts_to_parquet()`: Converts facts to DataFrame and saves as Parquet

**Extraction Strategy**:
1. Parse HTML tables for structured financial data
2. Fallback to text lines containing financial indicators ($, %)
3. Returns exactly 10 facts in standardized format

**Dependencies**: `beautifulsoup4`, `pandas`, `pyarrow`

### 5. Logger (`src/logger.py`)
**Purpose**: Centralized logging configuration for application monitoring.

**Features**:
- File-based logging with timestamps
- Prevents duplicate handlers
- Configurable log levels
- Tracks processing workflow and errors

### 6. Main Application (`src/app.py`)
**Purpose**: Orchestrates the entire workflow and provides entry point.

**Key Functions**:
- `process_ticker()`: **UPDATED** - Main processing pipeline accepting ProcessingState object
- Coordinates all components in sequence with state management
- **NEW**: Updates ProcessingState at each processing stage
- **NEW**: Persists state throughout the workflow
- **NEW**: Provides detailed progress tracking and error handling
- Handles errors and logging with state context

**Workflow**:
1. Setup logging
2. Initialize file watcher with ProcessingState callback
3. For each ProcessingState received:
   a. Update status to DOWNLOADING_SEC_FILING
   b. Download SEC filing and update state
   c. Update status to EXTRACTING_FACTS
   d. Extract facts and update state
   e. Update status to SAVING_PARQUET
   f. Save to Parquet and mark COMPLETED
   g. Log completion with processing duration
4. Handle errors by updating state and re-raising

**Enhanced Error Handling**:
- All errors are captured in ProcessingState
- State files are updated even when processing fails
- Detailed error messages and timestamps preserved

## Data Flow Architecture

### Input Layer
- **Format**: JSON files in `input/` directory
- **Schema**: `{"ticker": "SYMBOL"}`
- **Trigger**: File system events (creation)
- **NEW**: Files automatically moved to `input/processing/` for organized workflow
- **NEW**: State files created alongside processing files

### Processing Layer
- **Download**: SEC EDGAR API integration
- **Parse**: HTML/TXT document processing
- **Extract**: Financial fact identification and ranking
- **Transform**: Structured data conversion
- **NEW**: Complete state tracking through ProcessingState system
- **NEW**: Persistent state management in JSON format

### State Management Layer (NEW)
- **Purpose**: Track complete processing lifecycle
- **Format**: JSON state files in `input/processing/`
- **Schema**: ProcessingState with timestamps, file paths, status, metadata
- **Persistence**: Automatic state saving at each processing stage
- **Recovery**: State files enable process monitoring and recovery

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
│   ├── app.py              # Main orchestrator (UPDATED: ProcessingState integration)
│   ├── file_watcher.py     # File system monitoring (UPDATED: file moving + state mgmt)
│   ├── processing_state.py # NEW: Processing state management
│   ├── sec_edgar_downloader.py  # SEC data fetching
│   ├── fact_extractor.py   # Document parsing
│   └── logger.py           # Logging utilities
├── tests/
│   ├── test_app.py         # Integration tests (UPDATED: ProcessingState tests)
│   ├── test_file_watcher.py # File monitoring tests (UPDATED: state management tests)
│   ├── test_processing_state.py # NEW: ProcessingState unit tests
│   ├── test_sec_edgar_downloader.py # Download tests
│   └── test_fact_extractor.py # Extraction tests
├── input/                  # Ticker JSON files (monitored)
│   └── processing/         # NEW: Processing folder with moved files + state files
├── output/                 # Parquet results
├── sec-edgar-filings/      # Downloaded SEC filings
├── analyze_parquet_pyspark.ipynb # Analysis notebook
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Processing Workflow Example

### Example: Processing AAPL ticker file

1. **File Discovery**
   ```
   User creates: input/aapl.json → {"ticker": "AAPL"}
   ```

2. **File Processing Initiation**
   ```
   TickerFileHandler detects file
   → Creates ProcessingState(ticker="AAPL", status=DISCOVERED)
   → Moves file: input/aapl.json → input/processing/aapl.json
   → Creates state file: input/processing/aapl.state.json
   → Updates status: MOVED_TO_PROCESSING
   → Calls process_ticker(processing_state)
   ```

3. **SEC Filing Download**
   ```
   process_ticker() updates status: DOWNLOADING_SEC_FILING
   → Downloads SEC filing from EDGAR
   → Updates state: status=SEC_FILING_DOWNLOADED, sec_filing_path="/path/to/filing"
   → Saves state to aapl.state.json
   ```

4. **Fact Extraction**
   ```
   Updates status: EXTRACTING_FACTS
   → Extracts facts from SEC filing
   → Updates status: FACTS_EXTRACTED
   → Stores metadata: facts_count=10
   → Saves state to aapl.state.json
   ```

5. **Parquet Generation**
   ```
   Updates status: SAVING_PARQUET
   → Saves facts to output/AAPL_facts.parquet
   → Updates status: COMPLETED
   → Records parquet_output_path and processing duration
   → Final state save to aapl.state.json
   ```

6. **Final State File Example**
   ```json
   {
     "ticker": "AAPL",
     "original_file_path": "/backend/input/aapl.json",
     "processing_file_path": "/backend/input/processing/aapl.json",
     "state_file_path": "/backend/input/processing/aapl.state.json",
     "status": "completed",
     "created_at": "2025-09-10T10:00:00",
     "updated_at": "2025-09-10T10:05:30",
     "sec_filing_path": "/backend/sec-edgar-filings/AAPL/10-Q/filing.txt",
     "parquet_output_path": "/backend/output/AAPL_facts.parquet",
     "error_message": null,
     "metadata": {
       "facts_count": 10,
       "processing_duration": 330.0
     }
   }
   ```

## Benefits of State Management

### Monitoring and Observability
- Real-time processing status visibility
- Complete processing history and timeline
- Error tracking with detailed context
- Performance metrics (processing duration)

### Recovery and Reliability
- Process restart capability from any stage
- Failed processing identification and retry
- Complete audit trail for debugging
- Workflow orchestration support

### Operations and Maintenance
- Processing queue monitoring
- Performance optimization insights
- Error pattern analysis
- Capacity planning data

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
