# C4 Architecture Documentation

This directory contains PlantUML C4 model diagrams for the Predictive Trading Python App, documenting the system architecture at multiple levels of detail.

## Diagrams Overview

### [System Context Diagram](c4-context.puml)
Shows the system boundary and external actors/systems that interact with the Predictive Trading App.

**Key Elements:**
- User (analyst/trader)
- Predictive Trading App (main system)
- SEC EDGAR (external data source)
- File System (storage)

### [Container Diagram](c4-container.puml)
Shows the high-level technology choices and how containers communicate within the system.

**Key Containers:**
- File Watcher (Python watchdog)
- State Manager (Python)
- Processing Functions (Pure Python functions)
- SEC Downloader (sec-edgar-downloader)
- Fact Extractor (BeautifulSoup)
- Data Storage (Parquet files)
- Logger (Python logging)

### [Component Diagram](c4-component.puml)
Shows the internal structure of the main containers and how components interact.

**Key Components:**
- Main Application (app.py)
- Ticker File Handler (file monitoring)
- Processing State (data model)
- State Manager (orchestration)
- Processing Functions (business logic)
- External Service Adapters

### [Code Diagram](c4-code.puml)
Shows the detailed implementation structure of the core processing architecture.

**Key Code Elements:**
- Pure Data Model (ProcessingState, ProcessingStatus)
- Pure Processing Functions (functional approach)
- State Management & Orchestration (StateManager)
- Application Layer (integration points)

### [Deployment Diagram](c4-deployment.puml)
Shows how the software is deployed in the development environment.

**Key Deployment Elements:**
- Dev Container (Docker)
- Python Runtime (3.11.11)
- File System (Linux)
- Python Dependencies (pip packages)
- External Services (SEC EDGAR)

## Additional Diagrams

### [Processing Workflow Sequence](sequence-processing-workflow.puml)
Shows the step-by-step interaction flow when processing a ticker file.

### [Processing State Lifecycle](state-processing-lifecycle.puml)
Shows the state machine for the processing lifecycle with all possible transitions.

### [Class Diagram](class-diagram.puml)
Shows the detailed class structure and relationships between core components.

## Architecture Principles

### Separation of Concerns
The architecture separates:
1. **Pure Data Model** - No business logic, only data and serialization
2. **Pure Functions** - Stateless processing functions
3. **State Management** - Orchestration and persistence
4. **External Integrations** - SEC API, file system, logging

### Functional Programming Approach
- All processing functions are pure (no side effects)
- State updates use immutable patterns (`dataclasses.replace`)
- Clear input/output contracts for all functions

### Testability
- Pure functions are easily unit testable
- State manager can be mocked for integration tests
- Clear separation enables focused testing

### Maintainability
- Single responsibility for each component
- Clear interfaces between layers
- Easy to extend with new processing steps

## Viewing the Diagrams

These PlantUML diagrams can be viewed using:

1. **VS Code**: Install PlantUML extension
2. **Online**: Copy content to [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
3. **Local**: Install PlantUML jar and generate PNG/SVG files
4. **GitHub**: Some viewers support PlantUML rendering

## Architecture Documentation References

- [Overall Architecture](../ARCHITECTURE.md) - Complete system documentation
- [Processing Architecture](../PROCESSING_ARCHITECTURE.md) - Detailed processing flow documentation
- [Source Code](../src/) - Implementation details

## Regenerating Diagrams

To update these diagrams:

1. Modify the `.puml` files as needed
2. Regenerate images using PlantUML
3. Update this documentation if structure changes
4. Ensure consistency across all diagram levels

The diagrams follow the C4 model conventions:
- **Context** - System level view
- **Containers** - High-level technology view  
- **Components** - Internal structure view
- **Code** - Implementation details view