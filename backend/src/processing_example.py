"""
Example usage of the refactored processing architecture.

This module demonstrates how to use the pure data ProcessingState,
processing functions, and StateManager in the new architecture.
"""

import os
from typing import Dict, Any

from .processing_state import ProcessingState, ProcessingStatus
from .state_manager import StateManager
from .processing_functions import (
    move_to_processing,
    download_sec_filing,
    extract_facts,
    save_parquet
)


def process_ticker_file(ticker: str, file_path: str, config: Dict[str, Any]) -> ProcessingState:
    """
    Process a ticker file using the new architecture.
    
    This function demonstrates the complete workflow using pure functions
    and state management separation.
    
    Args:
        ticker (str): Ticker symbol to process
        file_path (str): Path to the input JSON file
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        ProcessingState: Final processing state
    """
    # Initialize state manager
    state_manager = StateManager(config.get('state_dir', 'input/processing'))
    
    # Create initial processing state
    initial_state = ProcessingState(
        ticker=ticker,
        original_file_path=file_path
    )
    
    # Execute the complete workflow
    final_state = state_manager.execute_workflow(initial_state, config)
    
    return final_state


def process_single_step_example(ticker: str, file_path: str) -> None:
    """
    Example of processing individual steps manually.
    
    This demonstrates how to use individual processing functions
    and manage state manually.
    
    Args:
        ticker (str): Ticker symbol to process
        file_path (str): Path to the input JSON file
    """
    # Create initial state
    state = ProcessingState(
        ticker=ticker,
        original_file_path=file_path
    )
    
    # Initialize state manager for persistence
    state_manager = StateManager('input/processing')
    
    print(f"Starting processing for {ticker}")
    print(f"Initial status: {state.status.value}")
    
    # Step 1: Move to processing
    state = move_to_processing(state, 'input/processing')
    state_manager.save_state(state)
    print(f"After move: {state.status.value}")
    
    if state.has_error():
        print(f"Error: {state.error_message}")
        return
    
    # Step 2: Download SEC filing
    state = download_sec_filing(state, 'sec-edgar-filings')
    state_manager.save_state(state)
    print(f"After download: {state.status.value}")
    
    if state.has_error():
        print(f"Error: {state.error_message}")
        return
    
    # Step 3: Extract facts
    state = extract_facts(state)
    state_manager.save_state(state)
    print(f"After extraction: {state.status.value}")
    
    if state.has_error():
        print(f"Error: {state.error_message}")
        return
    
    # Step 4: Save parquet
    state = save_parquet(state, 'output')
    state_manager.save_state(state)
    print(f"Final status: {state.status.value}")
    
    if state.is_completed():
        print(f"Processing completed successfully!")
        print(f"Output file: {state.parquet_output_path}")
        duration = state.get_processing_duration()
        if duration:
            print(f"Processing took: {duration:.2f} seconds")


def batch_processing_example(config: Dict[str, Any]) -> None:
    """
    Example of batch processing multiple tickers.
    
    This demonstrates how to process multiple files and manage
    their states using the StateManager.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
    """
    state_manager = StateManager(config.get('state_dir', 'input/processing'))
    
    # Example ticker files to process
    ticker_files = [
        ('AAPL', 'input/entry/aapl.json'),
        ('MSFT', 'input/entry/msft.json'),
        ('GOOGL', 'input/entry/googl.json')
    ]
    
    results = []
    
    for ticker, file_path in ticker_files:
        print(f"\nProcessing {ticker}...")
        
        # Check if already being processed
        existing_state = state_manager.find_state_by_ticker(ticker)
        
        if existing_state:
            if existing_state.is_completed():
                print(f"{ticker} already completed")
                results.append(existing_state)
                continue
            elif existing_state.has_error():
                print(f"Retrying failed processing for {ticker}")
                final_state = state_manager.retry_failed_processing(ticker, config)
            else:
                print(f"Resuming processing for {ticker}")
                final_state = state_manager.execute_workflow(existing_state, config)
        else:
            # Create new processing state
            initial_state = ProcessingState(
                ticker=ticker,
                original_file_path=file_path
            )
            final_state = state_manager.execute_workflow(initial_state, config)
        
        results.append(final_state)
        
        # Print results
        if final_state.is_completed():
            print(f"{ticker} completed successfully")
        elif final_state.has_error():
            print(f"{ticker} failed: {final_state.error_message}")
        else:
            print(f"{ticker} in progress: {final_state.status.value}")
    
    # Summary
    completed = sum(1 for state in results if state.is_completed())
    failed = sum(1 for state in results if state.has_error())
    in_progress = len(results) - completed - failed
    
    print(f"\n=== Batch Processing Summary ===")
    print(f"Total files: {len(results)}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"In Progress: {in_progress}")


def monitoring_example() -> None:
    """
    Example of monitoring processing states.
    
    This demonstrates how to query and monitor the status
    of processing across multiple tickers.
    """
    state_manager = StateManager('input/processing')
    
    # Get all states
    all_states = state_manager.list_states()
    
    print("=== Processing Status Overview ===")
    
    # Group by status
    status_groups = {}
    for state in all_states:
        status = state.status
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(state)
    
    for status, states in status_groups.items():
        print(f"\n{status.value.upper()}: {len(states)} tickers")
        for state in states:
            print(f"  - {state.ticker}")
            if state.has_error():
                print(f"    Error: {state.error_message}")
    
    # Show processing durations for completed
    completed_states = status_groups.get(ProcessingStatus.COMPLETED, [])
    if completed_states:
        print(f"\n=== Completed Processing Times ===")
        for state in completed_states:
            duration = state.get_processing_duration()
            if duration:
                print(f"{state.ticker}: {duration:.2f} seconds")


if __name__ == "__main__":
    # Example configuration
    config = {
        'state_dir': 'input/processing',
        'processing_dir': 'input/processing',
        'sec_filings_dir': 'sec-edgar-filings',
        'output_dir': 'output'
    }
    
    # Run examples
    print("=== Single File Processing ===")
    final_state = process_ticker_file('AAPL', 'input/entry/aapl.json', config)
    print(f"Final status: {final_state.status.value}")
    
    print("\n=== Single Step Processing ===")
    process_single_step_example('MSFT', 'input/entry/msft.json')
    
    print("\n=== Batch Processing ===")
    batch_processing_example(config)
    
    print("\n=== Monitoring ===")
    monitoring_example()
