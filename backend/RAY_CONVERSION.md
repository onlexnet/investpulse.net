# Ray Actor Conversion for Ticker Processing

This document describes the conversion of the ticker processing system from a sequential architecture to a distributed Ray actor-based architecture.

## Overview

The system has been converted to use Ray actors for distributed processing, enabling:
- **Parallel processing** of multiple tickers simultaneously
- **Fault tolerance** with actor-based error handling
- **Scalability** across multiple machines or cores
- **Resource management** with configurable worker pools
- **State persistence** with distributed state management

## Architecture

### Ray Actors

1. **RayStateManager** (`ray_state_manager.py`)
   - Manages processing state persistence
   - Provides in-memory caching for performance
   - Handles state serialization/deserialization
   - Supports distributed state queries

2. **RayProcessingWorker** (`ray_processing_worker.py`)
   - Executes individual processing steps
   - Provides worker statistics and monitoring
   - Handles step-level error recovery

3. **RayProcessingPool** (`ray_processing_worker.py`)
   - Manages a pool of processing workers
   - Implements round-robin task distribution
   - Provides pool-level statistics

4. **RayWorkflowOrchestrator** (`ray_workflow_orchestrator.py`)
   - Coordinates the complete processing workflow
   - Manages asynchronous task execution
   - Provides comprehensive monitoring and statistics
   - Handles retry logic for failed processing

### Configuration

Ray configuration is managed in `ray_config.py`:
- Environment-based configuration
- Development and production presets
- Cluster resource management
- Dashboard and logging configuration

## Usage

### Basic Usage

```python
import ray
from src.ray_config import initialize_ray, DEVELOPMENT_CONFIG
from src.ray_workflow_orchestrator import RayWorkflowOrchestrator

# Initialize Ray
initialize_ray(DEVELOPMENT_CONFIG)

# Create orchestrator
config = {
    'state_dir': 'processing',
    'processing_dir': 'processing',
    'sec_filings_dir': 'sec-edgar-filings',
    'output_dir': 'output'
}

orchestrator = RayWorkflowOrchestrator.remote(
    config=config,
    worker_pool_size=4
)

# Process a ticker
task_ref = orchestrator.process_ticker_async.remote('aapl.json', 'AAPL')
final_state = ray.get(task_ref)
```

### Batch Processing

```python
# Process multiple tickers concurrently
tickers = ['AAPL', 'MSFT', 'GOOGL']
tasks = {}

for ticker in tickers:
    file_path = f"{ticker.lower()}.json"
    task_ref = orchestrator.process_ticker_async.remote(file_path, ticker)
    tasks[ticker] = task_ref

# Wait for completion
results = orchestrator.wait_for_completion.remote(tickers, timeout=300)
final_results = ray.get(results)
```

### Monitoring

```python
# Get processing status
status_ref = orchestrator.get_processing_status.remote()
status = ray.get(status_ref)

print(f"Active tasks: {status['orchestrator']['active_tasks']}")
print(f"Completed: {status['orchestrator']['completed_tasks']}")
print(f"Throughput: {status['orchestrator']['throughput_per_minute']:.2f}/min")
```

## Ray Dashboard

Access the Ray dashboard at `http://localhost:8265` to monitor:
- Cluster resources and utilization
- Active tasks and actors
- Memory usage and object store
- Task execution timeline
- Actor lifecycle and logs

## Environment Variables

Configure Ray behavior using environment variables:

```bash
# Ray cluster settings
export RAY_ADDRESS=""                    # Local cluster (default)
export RAY_NAMESPACE="ticker-processing" # Namespace for isolation

# Resource limits
export RAY_NUM_CPUS=4                   # Number of CPUs to use
export RAY_NUM_GPUS=0                   # Number of GPUs to use
export RAY_MEMORY_MB=4096               # Memory limit in MB

# Dashboard settings
export RAY_DASHBOARD_HOST="0.0.0.0"     # Dashboard host
export RAY_DASHBOARD_PORT=8265          # Dashboard port

# Logging
export RAY_LOGGING_LEVEL="INFO"         # Logging level
export RAY_LOG_TO_DRIVER="true"         # Log to driver process
```

## Running the System

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python src/app.py

# Or run the example script
python src/ray_example.py
```

### Production Mode

```bash
# Set production environment variables
export RAY_LOGGING_LEVEL="WARNING"
export RAY_LOG_TO_DRIVER="false"
export RAY_NAMESPACE="ticker-processing-prod"

# Run with more workers
export RAY_NUM_CPUS=8

python src/app.py
```

## Performance Benefits

### Concurrency
- **Before**: Sequential processing of one ticker at a time
- **After**: Parallel processing of multiple tickers simultaneously

### Scalability
- **Before**: Limited to single machine resources
- **After**: Can scale across multiple machines in a Ray cluster

### Fault Tolerance
- **Before**: Single point of failure
- **After**: Actor-based isolation with automatic restart capabilities

### Resource Utilization
- **Before**: CPU and memory underutilization
- **After**: Optimal resource allocation with configurable worker pools

## Monitoring and Debugging

### Actor Status
```python
# Check actor health
actors = ray.list_actors()
for actor in actors:
    print(f"Actor: {actor['class_name']}, State: {actor['state']}")
```

### Resource Usage
```python
# Check cluster resources
resources = ray.cluster_resources()
available = ray.available_resources()

print(f"Total CPUs: {resources.get('CPU', 0)}")
print(f"Available CPUs: {available.get('CPU', 0)}")
```

### Task Profiling
Use Ray's built-in profiling tools:
```python
# Enable profiling
ray.timeline('ray_timeline.json')

# View in Chrome: chrome://tracing/
```

## Migration Notes

### Key Changes
1. **State Management**: `StateManager` → `RayStateManager` (actor-based)
2. **Processing**: Direct function calls → Ray actor method calls
3. **Workflow**: Sequential execution → Asynchronous task coordination
4. **Error Handling**: Local error handling → Distributed error recovery

### Compatibility
- All original processing functions remain unchanged (pure functions)
- Processing states and status enums are unchanged
- Configuration structure is preserved
- File I/O and data formats are unchanged

### Breaking Changes
- Main application now requires Ray initialization
- Processing is asynchronous by default
- Error handling includes actor-specific error messages
- Resource requirements include Ray dependencies

## Troubleshooting

### Common Issues

1. **Ray Initialization Failure**
   ```
   Error: Failed to initialize Ray
   Solution: Check available resources and port conflicts
   ```

2. **Actor Creation Timeout**
   ```
   Error: Failed to create workflow orchestrator
   Solution: Increase available CPU/memory resources
   ```

3. **Task Timeout**
   ```
   Error: ray.exceptions.GetTimeoutError
   Solution: Increase task timeout or optimize processing functions
   ```

### Debug Mode
Enable verbose logging:
```bash
export RAY_LOGGING_LEVEL="DEBUG"
export RAY_LOG_TO_DRIVER="true"
```

### Resource Monitoring
Monitor resource usage:
```bash
# Check Ray processes
ps aux | grep ray

# Monitor memory usage
watch -n 1 'ray status'
```

## Future Enhancements

1. **Auto-scaling**: Implement dynamic worker pool sizing
2. **Checkpointing**: Add periodic state checkpoints for long-running tasks
3. **Priority Queues**: Implement task prioritization
4. **Distributed Storage**: Use Ray's distributed object store for large data
5. **Multi-cluster**: Support processing across multiple Ray clusters