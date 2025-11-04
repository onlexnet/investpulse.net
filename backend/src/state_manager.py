"""
State management for processing workflow.

This module provides the StateManager class that handles reading and writing
processing states, orchestrating the workflow by calling processing functions.
"""

import json
import os
from typing import Optional, Callable, Dict, Any, List

from .processing_state import ProcessingState, ProcessingStatus
from .processing_functions import (
    move_to_processing, 
    download_sec_filing, 
    extract_facts, 
    save_parquet,
    handle_error
)


class StateManager:
    """
    Manages processing state persistence and workflow orchestration.
    
    This class handles reading states from disk, calling processing functions,
    and writing updated states back to disk. It acts as the coordinator between
    the pure data model and processing functions.
    """
    
    def __init__(self, state_dir: str):
        """
        Initialize the state manager.
        
        Args:
            state_dir (str): Directory to store state files
        """
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
    
    def save_state(self, state: ProcessingState) -> str:
        """
        Save processing state to disk.
        
        Args:
            state (ProcessingState): State to save
            
        Returns:
            str: Path where the state was saved
        """
        if state.state_file_path is None:
            state_filename = f"{state.ticker}_state.json"
            state.state_file_path = os.path.join(self.state_dir, state_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(state.state_file_path), exist_ok=True)
        
        with open(state.state_file_path, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
        
        return state.state_file_path
    
    def load_state(self, state_file_path: str) -> ProcessingState:
        """
        Load processing state from disk.
        
        Args:
            state_file_path (str): Path to the state file
            
        Returns:
            ProcessingState: Loaded state
            
        Raises:
            FileNotFoundError: If the state file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(state_file_path, 'r') as f:
            data = json.load(f)
        
        state = ProcessingState.from_dict(data)
        state.state_file_path = state_file_path
        return state
    
    def find_state_by_ticker(self, ticker: str) -> Optional[ProcessingState]:
        """
        Find existing state file by ticker symbol.
        
        Args:
            ticker (str): Ticker symbol to search for
            
        Returns:
            Optional[ProcessingState]: Loaded state if found, None otherwise
        """
        state_filename = f"{ticker}_state.json"
        state_path = os.path.join(self.state_dir, state_filename)
        
        if os.path.exists(state_path):
            return self.load_state(state_path)
        return None
    
    def list_states(self, status_filter: Optional[ProcessingStatus] = None) -> List[ProcessingState]:
        """
        List all states in the state directory.
        
        Args:
            status_filter (Optional[ProcessingStatus]): Filter by status if provided
            
        Returns:
            List[ProcessingState]: List of states matching the filter
        """
        states = []
        
        for filename in os.listdir(self.state_dir):
            if filename.endswith('_state.json'):
                try:
                    state_path = os.path.join(self.state_dir, filename)
                    state = self.load_state(state_path)
                    
                    if status_filter is None or state.status == status_filter:
                        states.append(state)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip corrupted state files
                    continue
        
        return states
    
    def process_step(self, state: ProcessingState, 
                    processing_func: Callable[..., ProcessingState],
                    *args, **kwargs) -> ProcessingState:
        """
        Execute a processing step and save the updated state.
        
        Args:
            state (ProcessingState): Current state
            processing_func (Callable): Processing function to execute
            *args: Additional arguments for the processing function
            **kwargs: Additional keyword arguments for the processing function
            
        Returns:
            ProcessingState: Updated state after processing
        """
        try:
            # Execute the processing function
            updated_state = processing_func(state, *args, **kwargs)
            
            # Save the updated state
            self.save_state(updated_state)
            
            return updated_state
            
        except Exception as e:
            # Handle unexpected errors
            error_state = handle_error(state, f"Unexpected error in processing: {str(e)}")
            self.save_state(error_state)
            return error_state
    
    def execute_workflow(self, initial_state: ProcessingState, 
                        config: Dict[str, Any]) -> ProcessingState:
        """
        Execute the complete processing workflow.
        
        This method orchestrates the entire processing pipeline from start
        to finish, handling each step and updating state accordingly.
        
        Args:
            initial_state (ProcessingState): Starting state
            config (Dict[str, Any]): Configuration for processing directories
            
        Returns:
            ProcessingState: Final state after workflow completion
        """
        current_state = initial_state
        
        # Save initial state
        self.save_state(current_state)
        
        # Step 1: Move to processing
        if current_state.status == ProcessingStatus.DISCOVERED:
            current_state = self.process_step(
                current_state, 
                move_to_processing, 
                config.get('processing_dir', 'input/processing')
            )
            
            if current_state.has_error():
                return current_state
        
        # Step 2: Download SEC filing
        if current_state.status == ProcessingStatus.MOVED_TO_PROCESSING:
            current_state = self.process_step(
                current_state, 
                download_sec_filing, 
                config.get('sec_filings_dir', 'sec-edgar-filings')
            )
            
            if current_state.has_error():
                return current_state
        
        # Step 3: Extract facts
        if current_state.status == ProcessingStatus.SEC_FILING_DOWNLOADED:
            current_state = self.process_step(
                current_state, 
                extract_facts
            )
            
            if current_state.has_error():
                return current_state
        
        # Step 4: Save parquet
        if current_state.status == ProcessingStatus.FACTS_EXTRACTED:
            current_state = self.process_step(
                current_state, 
                save_parquet, 
                config.get('output_dir', 'output')
            )
        
        return current_state
    
    def retry_failed_processing(self, ticker: str, config: Dict[str, Any]) -> Optional[ProcessingState]:
        """
        Retry processing for a failed ticker.
        
        This method loads the existing state for a ticker and retries processing
        from the appropriate step based on the current state.
        
        Args:
            ticker (str): Ticker symbol to retry
            config (Dict[str, Any]): Configuration for processing directories
            
        Returns:
            Optional[ProcessingState]: Final state after retry, None if not found
        """
        existing_state = self.find_state_by_ticker(ticker)
        
        if existing_state is None:
            return None
        
        if not existing_state.has_error():
            # Nothing to retry
            return existing_state
        
        # Reset the error state and continue processing
        from .processing_functions import reset_error
        reset_state = reset_error(existing_state)
        
        return self.execute_workflow(reset_state, config)
    
    def cleanup_completed_states(self, keep_days: int = 30) -> int:
        """
        Clean up old completed state files.
        
        This method removes state files for completed processing that are
        older than the specified number of days.
        
        Args:
            keep_days (int): Number of days to keep completed states
            
        Returns:
            int: Number of state files removed
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        completed_states = self.list_states(ProcessingStatus.COMPLETED)
        
        for state in completed_states:
            if state.updated_at < cutoff_date:
                try:
                    os.remove(state.state_file_path)
                    removed_count += 1
                except OSError:
                    # Skip if file can't be removed
                    continue
        
        return removed_count
