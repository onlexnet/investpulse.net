"""
Example script demonstrating Ray actor usage for ticker processing.

This script shows how to use the Ray-based ticker processing system
for batch processing and monitoring.
"""

import os
import ray
import json
import time
from typing import List, Dict, Any

from src.ray_config import initialize_ray, shutdown_ray, DEVELOPMENT_CONFIG
from src.ray_workflow_orchestrator import RayWorkflowOrchestrator
from src.processing_state import ProcessingState, ProcessingStatus


def create_sample_ticker_files(input_dir: str, tickers: List[str]) -> List[str]:
    """
    Create sample ticker JSON files for testing.
    
    Args:
        input_dir (str): Directory to create files in
        tickers (List[str]): List of ticker symbols
        
    Returns:
        List[str]: List of created file paths
    """
    os.makedirs(input_dir, exist_ok=True)
    file_paths = []
    
    for ticker in tickers:
        file_path = os.path.join(input_dir, f"{ticker.lower()}.json")
        sample_data = {
            "ticker": ticker,
            "timestamp": int(time.time()),
            "source": "example"
        }
        
        with open(file_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        file_paths.append(file_path)
    
    return file_paths


def batch_process_tickers(orchestrator, tickers: List[str], input_dir: str) -> Dict[str, ProcessingState]:
    """
    Process multiple tickers in batch using Ray actors.
    
    Args:
        orchestrator: Ray orchestrator actor
        tickers (List[str]): List of ticker symbols to process
        input_dir (str): Directory containing ticker files
        
    Returns:
        Dict[str, ProcessingState]: Final states for each ticker
    """
    print(f"Starting batch processing for {len(tickers)} tickers...")
    
    # Submit all tasks asynchronously
    task_refs = {}
    for ticker in tickers:
        file_path = os.path.join(input_dir, f"{ticker.lower()}.json")
        if os.path.exists(file_path):
            task_ref = orchestrator.process_ticker_async.remote(file_path, ticker)
            task_refs[ticker] = task_ref
            print(f"Submitted task for ticker: {ticker}")
    
    # Wait for all tasks to complete
    print("Waiting for all tasks to complete...")
    results = {}
    
    for ticker, task_ref in task_refs.items():
        try:
            final_state = ray.get(task_ref, timeout=60)  # 60 second timeout per task
            results[ticker] = final_state
            
            if final_state.is_completed():
                duration = final_state.get_processing_duration()
                print(f"✓ {ticker}: Completed in {duration:.2f}s")
            elif final_state.has_error():
                print(f"✗ {ticker}: Error - {final_state.error_message}")
            else:
                print(f"⚠ {ticker}: Incomplete - {final_state.status.value}")
                
        except ray.exceptions.GetTimeoutError:
            print(f"⏱ {ticker}: Timeout")
        except Exception as e:
            print(f"✗ {ticker}: Exception - {e}")
    
    return results


def monitor_processing_progress(orchestrator, interval: int = 5, duration: int = 60):
    """
    Monitor processing progress for a specified duration.
    
    Args:
        orchestrator: Ray orchestrator actor
        interval (int): Monitoring interval in seconds
        duration (int): Total monitoring duration in seconds
    """
    print(f"Monitoring processing for {duration} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            status_ref = orchestrator.get_processing_status.remote()
            status = ray.get(status_ref, timeout=5)
            
            orchestrator_stats = status.get('orchestrator', {})
            state_stats = status.get('state_manager', {})
            
            print(f"\n--- Processing Status ---")
            print(f"Active tasks: {orchestrator_stats.get('active_tasks', 0)}")
            print(f"Completed: {orchestrator_stats.get('completed_tasks', 0)}")
            print(f"Failed: {orchestrator_stats.get('failed_tasks', 0)}")
            print(f"Total processed: {orchestrator_stats.get('total_processed', 0)}")
            print(f"Total errors: {orchestrator_stats.get('total_errors', 0)}")
            print(f"Throughput: {orchestrator_stats.get('throughput_per_minute', 0):.2f}/min")
            
            by_status = state_stats.get('by_status', {})
            for status_name, count in by_status.items():
                if count > 0:
                    print(f"{status_name}: {count}")
            
        except Exception as e:
            print(f"Error getting status: {e}")
        
        time.sleep(interval)


def main():
    """Main example function."""
    print("Ray Ticker Processing Example")
    print("=" * 40)
    
    # Configuration
    INPUT_DIR = "example_input"
    PROCESSING_CONFIG = {
        'state_dir': 'example_processing',
        'processing_dir': 'example_processing',
        'sec_filings_dir': 'example_sec_filings',
        'output_dir': 'example_output'
    }
    
    # Sample tickers to process
    SAMPLE_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    # Create directories
    for dir_path in PROCESSING_CONFIG.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Initialize Ray
    print("\n1. Initializing Ray...")
    if not initialize_ray(DEVELOPMENT_CONFIG):
        print("Failed to initialize Ray")
        return
    
    print(f"Ray cluster resources: {ray.cluster_resources()}")
    
    try:
        # Create orchestrator
        print("\n2. Creating workflow orchestrator...")
        orchestrator = RayWorkflowOrchestrator.remote(
            config=PROCESSING_CONFIG,
            worker_pool_size=3
        )
        
        # Create sample files
        print("\n3. Creating sample ticker files...")
        file_paths = create_sample_ticker_files(INPUT_DIR, SAMPLE_TICKERS)
        print(f"Created {len(file_paths)} sample files")
        
        # Example 1: Process single ticker
        print("\n4. Example 1: Single ticker processing...")
        single_ticker = SAMPLE_TICKERS[0]
        single_file = file_paths[0]
        
        task_ref = orchestrator.process_ticker_async.remote(single_file, single_ticker)
        result = ray.get(task_ref)
        
        print(f"Single ticker result: {result.status.value}")
        
        # Example 2: Batch processing
        print("\n5. Example 2: Batch processing...")
        batch_results = batch_process_tickers(orchestrator, SAMPLE_TICKERS[1:], INPUT_DIR)
        
        successful = sum(1 for state in batch_results.values() if state.is_completed())
        failed = sum(1 for state in batch_results.values() if state.has_error())
        
        print(f"\nBatch results: {successful} successful, {failed} failed")
        
        # Example 3: Monitor processing
        print("\n6. Example 3: Processing status...")
        status_ref = orchestrator.get_processing_status.remote()
        final_status = ray.get(status_ref)
        print(f"Final orchestrator stats: {final_status.get('orchestrator', {})}")
        
        # Cleanup
        print("\n7. Cleaning up resources...")
        cleanup_ref = orchestrator.cleanup_resources.remote()
        cleanup_stats = ray.get(cleanup_ref)
        print(f"Cleanup stats: {cleanup_stats}")
        
        # Shutdown orchestrator
        ray.get(orchestrator.shutdown.remote())
        
    except Exception as e:
        print(f"Error in main: {e}")
    
    finally:
        # Shutdown Ray
        print("\n8. Shutting down Ray...")
        shutdown_ray()
        print("Example completed!")


if __name__ == "__main__":
    main()