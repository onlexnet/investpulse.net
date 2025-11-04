"""
Ray actor-based state management for processing workflow.

This module provides the RayStateManager actor that handles reading and writing
processing states in a distributed manner using Ray actors for scalability and fault tolerance.
"""

import json
import os
import ray
from typing import Optional, Dict, Any, List

from .processing_state import ProcessingState, ProcessingStatus
from .processing_functions import (
    move_to_processing, 
    download_sec_filing, 
    extract_facts, 
    save_parquet,
    handle_error
)


class RayStateManager:
    """
    Ray actor for managing processing state persistence and workflow orchestration.
    
    This actor handles reading states from disk, coordinating processing steps,
    and writing updated states back to disk in a distributed environment.
    """
    
    def __init__(self, state_dir: str):
        """
        Initialize the Ray state manager actor.
        
        Args:
            state_dir (str): Directory to store state files
        """
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
        
        # In-memory cache for active states to reduce disk I/O
        self._state_cache: Dict[str, ProcessingState] = {}
    
    @ray.method
    def save_state(self, state: ProcessingState) -> str:
        """
        Save processing state to disk and update cache.
        
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
        
        # Save to disk
        with open(state.state_file_path, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
        
        # Update cache
        self._state_cache[state.ticker] = state
        
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
        
        # Update cache
        self._state_cache[state.ticker] = state
        
        return state
    
    @ray.method
    def find_state_by_ticker(self, ticker: str) -> Optional[ProcessingState]:
        """
        Find existing state by ticker symbol, checking cache first.
        
        Args:
            ticker (str): Ticker symbol to search for
            
        Returns:
            Optional[ProcessingState]: Loaded state if found, None otherwise
        """
        # Check cache first
        if ticker in self._state_cache:
            return self._state_cache[ticker]
        
        # Check disk
        state_filename = f"{ticker}_state.json"
        state_path = os.path.join(self.state_dir, state_filename)
        
        if os.path.exists(state_path):
            return self.load_state(state_path)
        return None
    
    @ray.method
    def list_states(self, status_filter: Optional[ProcessingStatus] = None) -> List[ProcessingState]:
        return self._list_states(status_filter)

    def _list_states(self, status_filter: Optional[ProcessingStatus] = None) -> List[ProcessingState]:
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
    
    @ray.method
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current processing states.
        
        Returns:
            Dict[str, Any]: Statistics including counts by status
        """
        all_states = self._list_states()
        stats = {
            'total_states': len(all_states),
            'by_status': {},
            'cached_states': len(self._state_cache)
        }
        
        for status in ProcessingStatus:
            count = len([s for s in all_states if s.status == status])
            stats['by_status'][status.value] = count
        
        return stats
    
    def cleanup_cache(self) -> int:
        """
        Clean up the in-memory cache of completed or errored states.
        
        Returns:
            int: Number of states removed from cache
        """
        initial_count = len(self._state_cache)
        
        # Remove completed or errored states from cache
        tickers_to_remove = []
        for ticker, state in self._state_cache.items():
            if state.status in [ProcessingStatus.COMPLETED, ProcessingStatus.ERROR]:
                tickers_to_remove.append(ticker)
        
        for ticker in tickers_to_remove:
            del self._state_cache[ticker]
        
        return initial_count - len(self._state_cache)
    
    def cleanup_completed_states(self, keep_days: int = 30) -> int:
        """
        Clean up old completed state files.
        
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
                    # Remove from cache if present
                    if state.ticker in self._state_cache:
                        del self._state_cache[state.ticker]
                    removed_count += 1
                except OSError:
                    # Skip if file can't be removed
                    continue
        
        return removed_count