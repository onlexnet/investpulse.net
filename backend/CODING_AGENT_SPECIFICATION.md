# Coding Agent Specification for InvestPulse Financial Data Processing System

## Overview

This specification defines a coding agent for the InvestPulse financial data processing system, a distributed Python application that monitors financial ticker symbols, downloads SEC EDGAR filings, extracts financial facts, and stores them in Parquet format for analysis. The agent should be capable of understanding and modifying this complex, event-driven system that uses Ray for distributed processing.

## System Architecture Understanding

### Core Architecture Principles

The system follows three main architectural principles:

1. **Pure Data Model**: Data structures with no business logic (ProcessingState)
2. **Pure Processing Functions**: Stateless functions that transform state
3. **State Management**: Handles persistence and workflow orchestration

### Key Components

#### 1. File Monitoring System
- **File Watcher** (`src/file_watcher.py`): Monitors `input/entry/` for JSON files containing ticker symbols
- **Event-Driven**: Uses filesystem events to trigger processing workflows
- **File Organization**: Moves files to `input/processing/` directory for structured workflow

#### 2. Processing State Management
- **ProcessingState** (`src/processing_state.py`): Pure data structure tracking processing lifecycle
- **ProcessingStatus Enum**: Defines 9 processing stages from DISCOVERED to COMPLETED/ERROR
- **State Persistence**: JSON serialization with automatic file management

#### 3. Pure Processing Functions
- **Processing Functions** (`src/processing_functions.py`): Stateless functions for each workflow step
- **Immutable Updates**: Uses `dataclasses.replace()` for state updates
- **Composable**: Functions can be tested and executed in isolation

#### 4. Distributed Processing (Ray)
- **RayWorkflowOrchestrator** (`src/ray_workflow_orchestrator.py`): Coordinates distributed workflows
- **RayStateManager** (`src/ray_state_manager.py`): Distributed state management with caching
- **RayProcessingWorker/Pool** (`src/ray_processing_worker.py`): Worker pool for parallel processing
- **Fault Tolerance**: Error handling, retry logic, and resource cleanup

#### 5. Data Processing Pipeline
- **SEC EDGAR Downloader** (`src/sec_edgar_downloader.py`): Downloads real SEC filings
- **Fact Extractor** (`src/fact_extractor.py`): Extracts financial facts from filings
- **Parquet Storage**: Saves processed data in Parquet format for analysis

## Coding Agent Capabilities

### 1. Code Understanding and Analysis

The agent must understand:

#### Architecture Patterns
- **Event-driven design** with file system monitoring
- **Actor model** using Ray for distributed processing
- **Pure functional processing** with immutable state updates
- **State machine pattern** with defined processing stages
- **Separation of concerns** between data, processing, and orchestration

#### Data Flow
```
JSON File → File Watcher → Processing State → SEC Download → Fact Extraction → Parquet Storage
```

#### Directory Structure
```
input/entry/           # Initial ticker files
input/processing/      # Files being processed + state files
sec-edgar-filings/     # Downloaded SEC filings
output/               # Final parquet files
```

#### Processing States
1. `DISCOVERED` → 2. `MOVED_TO_PROCESSING` → 3. `DOWNLOADING_SEC_FILING` → 
4. `SEC_FILING_DOWNLOADED` → 5. `EXTRACTING_FACTS` → 6. `FACTS_EXTRACTED` → 
7. `SAVING_PARQUET` → 8. `COMPLETED` (or `ERROR`)

### 2. Code Modification Capabilities

#### Adding New Processing Steps
- Create new pure functions in `processing_functions.py`
- Add corresponding status to `ProcessingStatus` enum
- Update workflow orchestrator to include new step
- Implement Ray worker methods for distributed execution

#### Enhancing State Management
- Extend `ProcessingState` dataclass with new fields
- Update serialization/deserialization methods
- Modify state file management and caching logic

#### Scaling and Performance
- Add new Ray actors for specialized processing
- Implement load balancing and resource optimization
- Add monitoring and metrics collection

#### Error Handling and Recovery
- Implement retry mechanisms with exponential backoff
- Add circuit breaker patterns for external services
- Create comprehensive error logging and alerting

### 3. Testing and Validation

#### Unit Testing Requirements
- Test pure functions in isolation
- Mock external dependencies (SEC EDGAR API)
- Validate state transitions and data integrity
- Test Ray actor communication and fault tolerance

#### Integration Testing
- End-to-end workflow testing
- File system monitoring and processing
- Distributed processing scenarios
- Error recovery and retry mechanisms

### 4. Development Standards

#### Python Coding Standards
- **PEP 8** compliance with 79-character line limits
- **Type hints** for all function parameters and return values
- **Docstrings** following PEP 257 conventions
- **Error handling** with clear exception messages

#### Code Organization
- **Modular design** with single-responsibility principle
- **Clear separation** between data, processing, and orchestration
- **Dependency injection** for configuration and external services
- **Immutable patterns** for state management

#### Documentation Requirements
- **Function docstrings** with parameters, return values, and examples
- **Class documentation** explaining purpose and usage patterns
- **Architecture decisions** documented with rationale
- **API documentation** for external interfaces

## Technical Dependencies

### Core Libraries
- **Ray**: Distributed computing framework
- **Watchdog**: File system monitoring
- **sec-edgar-downloader**: SEC filing downloads
- **Pandas/PyArrow**: Data processing and Parquet storage
- **BeautifulSoup4**: HTML/XML parsing for fact extraction
- **PySpark**: Large-scale data processing (optional)

### Development Tools
- **MyPy**: Static type checking
- **Pytest**: Unit and integration testing
- **Black/Flake8**: Code formatting and linting

### Infrastructure
- **Ubuntu 22.04** development environment
- **Docker** containerization support
- **Azure CLI** for cloud deployment
- **GitHub CLI** for repository management

## Agent Behavioral Guidelines

### 1. Code Generation Principles

#### Pure Function Preference
- Generate stateless functions that take state as input and return updated state
- Avoid side effects within processing functions
- Use `dataclasses.replace()` for immutable state updates

#### Ray Actor Design
- Create actors for stateful components (managers, pools, orchestrators)
- Implement proper shutdown and cleanup methods
- Add comprehensive error handling and logging

#### Configuration Management
- Use dependency injection for configuration
- Support both development and production configurations
- Externalize all environment-specific settings

### 2. Error Handling Strategy

#### Graceful Degradation
- Implement retry logic with exponential backoff
- Provide fallback mechanisms for external service failures
- Maintain system stability during partial failures

#### Comprehensive Logging
- Log all state transitions and processing steps
- Include correlation IDs for distributed tracing
- Provide clear error messages with context

#### Recovery Mechanisms
- Implement automatic retry for transient failures
- Provide manual retry capabilities for persistent errors
- Support workflow resumption from any processing stage

### 3. Performance Considerations

#### Distributed Processing
- Optimize task distribution across Ray workers
- Implement efficient caching strategies
- Monitor resource utilization and adjust accordingly

#### Data Processing
- Stream large files to avoid memory issues
- Use chunked processing for large datasets
- Optimize Parquet file structure for query performance

#### State Management
- Implement efficient state caching and persistence
- Minimize disk I/O through batching operations
- Use appropriate data structures for fast lookups

## Agent Integration Points

### 1. File System Integration
- Monitor multiple input directories
- Handle various file formats and naming conventions
- Implement robust file locking and concurrency control

### 2. External API Integration
- SEC EDGAR API for filing downloads
- Rate limiting and API key management
- Circuit breaker patterns for external service failures

### 3. Data Storage Integration
- Multiple output formats (Parquet, JSON, CSV)
- Database integration for metadata storage
- Cloud storage integration (Azure Blob Storage)

### 4. Monitoring Integration
- Metrics collection and reporting
- Health check endpoints
- Performance monitoring and alerting

## Validation and Testing Framework

### 1. Unit Test Coverage
- All pure functions must have 100% test coverage
- Mock external dependencies for isolated testing
- Test edge cases and error conditions

### 2. Integration Test Scenarios
- Complete workflow from file input to Parquet output
- Distributed processing with multiple workers
- Error scenarios and recovery mechanisms
- Performance testing with large datasets

### 3. Continuous Integration
- Automated testing on all pull requests
- Type checking with MyPy
- Code quality checks with linting tools
- Integration tests with sample data

## Future Enhancement Capabilities

### 1. Scalability Improvements
- Support for multiple data sources beyond SEC filings
- Real-time streaming data processing
- Auto-scaling based on workload

### 2. Feature Extensions
- Advanced financial fact extraction using ML models
- Data quality validation and enrichment
- Custom alerting and notification systems

### 3. Operational Enhancements
- Web-based monitoring dashboard
- RESTful API for external integrations
- Automated deployment and configuration management

## Summary

This coding agent specification provides a comprehensive framework for understanding and modifying the InvestPulse financial data processing system. The agent should be capable of:

1. **Understanding** the complex distributed architecture with Ray actors
2. **Modifying** code while maintaining architectural principles
3. **Testing** changes thoroughly with appropriate test coverage
4. **Scaling** the system for increased performance and reliability
5. **Maintaining** code quality and documentation standards

The agent must respect the existing architectural patterns while being able to enhance and extend the system's capabilities in a maintainable and scalable manner.