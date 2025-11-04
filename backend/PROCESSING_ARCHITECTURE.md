# Processing Architecture Documentation

## Overview

The refactored processing architecture separates concerns into three main components:

1. **Pure Data Model** (`processing_state.py`) - Contains only data structures and serialization
2. **Processing Functions** (`processing_functions.py`) - Pure functions that transform state
3. **State Management** (`state_manager.py`) - Handles persistence and workflow orchestration

## Architecture Principles

### 1. Pure Data Model

The `ProcessingState` class is now a pure data structure that:
- Contains only data fields and basic serialization methods
- Has no business logic or state mutation methods
- Provides utility methods for status checking and duration calculation
- Maintains the same enum values for all processing statuses

### 2. Pure Processing Functions

All processing logic is implemented as pure functions that:
- Take a `ProcessingState` as input
- Return a modified `ProcessingState` as output
- Handle a single processing step
- Are composable and testable in isolation
- Use `dataclasses.replace()` for immutable state updates

### 3. State Management

The `StateManager` class handles:
- Reading and writing state files to disk
- Orchestrating the workflow by calling processing functions
- Error handling and recovery
- Batch processing and monitoring

## Components

### ProcessingState (processing_state.py)

```python
@dataclass
class ProcessingState:
    """Pure data structure for processing state."""
    ticker: str
    original_file_path: str
    processing_file_path: Optional[str] = None
    state_file_path: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.DISCOVERED
    created_at: datetime = None
    updated_at: datetime = None
    sec_filing_path: Optional[str] = None
    parquet_output_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
```

**Key Methods:**
- `to_dict()` / `from_dict()` - JSON serialization
- `is_completed()` / `has_error()` - Status checking
- `get_processing_duration()` - Duration calculation

### Processing Functions (processing_functions.py)

Each function handles one step in the processing pipeline:

- `move_to_processing(state, processing_dir)` - Move file to processing directory
- `download_sec_filing(state, output_dir)` - Download SEC filing
- `extract_facts(state)` - Extract facts from filing
- `save_parquet(state, output_dir)` - Save data to parquet format
- `handle_error(state, error_message)` - Handle errors
- `reset_error(state)` - Reset error state for retry

**Function Signature:**
```python
def processing_function(state: ProcessingState, *args) -> ProcessingState:
    """Process one step and return updated state."""
    # Processing logic here
    return replace(state, ...)
```

### State Manager (state_manager.py)

The `StateManager` class provides:

```python
class StateManager:
    def __init__(self, state_dir: str)
    def save_state(self, state: ProcessingState) -> str
    def load_state(self, state_file_path: str) -> ProcessingState
    def find_state_by_ticker(self, ticker: str) -> Optional[ProcessingState]
    def list_states(self, status_filter: Optional[ProcessingStatus] = None) -> List[ProcessingState]
    def process_step(self, state: ProcessingState, processing_func: Callable, *args, **kwargs) -> ProcessingState
    def execute_workflow(self, initial_state: ProcessingState, config: Dict[str, Any]) -> ProcessingState
    def retry_failed_processing(self, ticker: str, config: Dict[str, Any]) -> Optional[ProcessingState]
    def cleanup_completed_states(self, keep_days: int = 30) -> int
```

## Usage Examples

### Basic Processing

```python
from src.state_manager import StateManager
from src.processing_state import ProcessingState

# Initialize state manager
state_manager = StateManager('input/processing')

# Create initial state
initial_state = ProcessingState(
    ticker='AAPL',
    original_file_path='input/entry/aapl.json'
)

# Execute complete workflow
config = {
    'processing_dir': 'input/processing',
    'sec_filings_dir': 'sec-edgar-filings',
    'output_dir': 'output'
}

final_state = state_manager.execute_workflow(initial_state, config)
```

### Manual Step Processing

```python
from src.processing_functions import move_to_processing, download_sec_filing

# Process individual steps
state = ProcessingState(ticker='MSFT', original_file_path='input/msft.json')

# Step 1: Move to processing
state = move_to_processing(state, 'input/processing')
state_manager.save_state(state)

# Step 2: Download SEC filing
state = download_sec_filing(state, 'sec-edgar-filings')
state_manager.save_state(state)
```

### Monitoring and Recovery

```python
# List all states by status
failed_states = state_manager.list_states(ProcessingStatus.ERROR)
completed_states = state_manager.list_states(ProcessingStatus.COMPLETED)

# Retry failed processing
for state in failed_states:
    final_state = state_manager.retry_failed_processing(state.ticker, config)
    
# Cleanup old completed states
removed_count = state_manager.cleanup_completed_states(keep_days=30)
```

## Benefits of New Architecture

### 1. Separation of Concerns
- Data model is pure and focused on data representation
- Processing logic is isolated in pure functions
- State management is centralized and consistent

### 2. Testability
- Each processing function can be tested in isolation
- State transformations are predictable and verifiable
- No side effects in the data model

### 3. Composability
- Functions can be combined in different workflows
- Easy to add new processing steps
- Workflow orchestration is flexible

### 4. Error Handling
- Centralized error handling in StateManager
- Automatic state persistence on errors
- Built-in retry mechanisms

### 5. Monitoring and Debugging
- Complete audit trail through state files
- Easy to query processing status
- Clear separation between data and operations

## Migration Guide

### From Old Architecture

The old architecture mixed data and behavior in the `ProcessingState` class:

```python
# Old way
processing_state.update_status(ProcessingStatus.DOWNLOADING_SEC_FILING)
processing_state.save_to_file()
```

### To New Architecture

The new architecture separates concerns:

```python
# New way
state = replace(state, status=ProcessingStatus.DOWNLOADING_SEC_FILING, updated_at=datetime.now())
state_manager.save_state(state)

# Or using processing functions
state = download_sec_filing(state, output_dir)
state_manager.save_state(state)
```

### Key Changes

1. **ProcessingState** - Removed all mutation methods (`update_status`, `save_to_file`, etc.)
2. **Processing Functions** - Created separate module with pure functions
3. **State Manager** - New class handles persistence and workflow orchestration
4. **App Integration** - Updated to use new architecture patterns

## File Structure

```
src/
├── processing_state.py      # Pure data model
├── processing_functions.py  # Pure processing functions
├── state_manager.py         # State persistence and workflow
├── processing_example.py    # Usage examples
├── app.py                   # Updated main application
└── file_watcher.py          # Updated file watcher
```

This architecture provides a clean separation of concerns, improved testability, and better maintainability while preserving all existing functionality.
