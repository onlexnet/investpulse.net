"""
Ray orchestrator for coordinating the complete processing workflow.

This module provides the RayWorkflowOrchestrator actor that coordinates
the entire processing pipeline using Ray actors for scalability and fault tolerance.
"""

import ray
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

import ray.exceptions

from .processing_state import ProcessingState, ProcessingStatus
from .ray_state_manager import RayStateManager
from .ray_processing_worker import DownloadSecFilingStep, ExtractFactsStep, MoveToProcessingStep, RayProcessingPool, ResetErrorStep, SaveParquetStep


class RayWorkflowOrchestrator:
    """
    Ray actor for orchestrating the complete processing workflow.
    
    This actor coordinates state management, worker pools, and workflow execution
    to process multiple tickers concurrently in a distributed manner.
    """
    
    def __init__(self, config: Dict[str, Any], worker_pool_size: int = 4):
        """
        Initialize the workflow orchestrator.
        
        Args:
            config (Dict[str, Any]): Configuration for processing directories
            worker_pool_size (int): Number of workers in the processing pool
        """
        self.config = config
        self.worker_pool_size = worker_pool_size
        
        # Initialize Ray actors
        self.state_manager = ray.remote(RayStateManager).remote(config['state_dir'])
        self.processing_pool = ray.remote(RayProcessingPool).remote(worker_pool_size)
        
        # Track active processing tasks
        self.active_tasks: Dict[str, ray.ObjectRef] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        
        # Orchestrator statistics
        self.total_processed = 0
        self.total_errors = 0
        self.start_time = datetime.now()
    
    @ray.method
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the orchestrator.
        
        Returns:
            Dict[str, Any]: Orchestrator statistics
        """
        runtime = (datetime.now() - self.start_time).total_seconds()
        return {
            'total_processed': self.total_processed,
            'total_errors': self.total_errors,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'runtime_seconds': runtime,
            'throughput_per_minute': (self.total_processed / runtime) * 60 if runtime > 0 else 0
        }
    
    @ray.method
    def process_ticker_async(self, file_path: str, ticker: str) -> ProcessingState:
        """
        Start asynchronous processing for a ticker.
        
        Args:
            file_path (str): Path to the ticker JSON file
            ticker (str): Ticker symbol
            
        Returns:
            ray.ObjectRef: Future containing the final processing state
        """
        # Check if already processing this ticker
        if ticker in self.active_tasks:
            task_ref = self.active_tasks[ticker]
            task = ray.get(task_ref)
            return task
        
        # Start processing task
        task = self._execute_workflow(file_path, ticker)
        task_ref = ray.put(task)
        self.active_tasks[ticker] = task_ref

        return task
    
    def _execute_workflow(self, file_path: str, ticker: str) -> ProcessingState:
        """
        Execute the complete workflow for a ticker asynchronously.
        
        Args:
            file_path (str): Path to the ticker JSON file
            ticker (str): Ticker symbol
            
        Returns:
            ProcessingState: Final processing state
        """
        try:
            # Check for existing state
            existing_state_ref = self.state_manager.find_state_by_ticker.remote(ticker)
            existing_state = ray.get(existing_state_ref)
            
            if existing_state:
                if existing_state.is_completed():
                    self._mark_task_completed(ticker)
                    return existing_state
                elif existing_state.has_error():
                    # Reset error and retry
                    reset_state_ref = self.processing_pool.process_step.remote(
                        existing_state,
                        ResetErrorStep()
                    )
                    current_state = ray.get(reset_state_ref)
                else:
                    current_state = existing_state
            else:
                # Create new processing state
                current_state = ProcessingState(
                    ticker=ticker,
                    original_file_path=file_path
                )
            
            # Save initial state
            save_ref = self.state_manager.save_state.remote(current_state)
            ray.get(save_ref)
            
            # Execute workflow steps
            current_state = self._execute_workflow_steps(current_state)
            
            # Mark task as completed or failed
            if current_state.is_completed():
                self._mark_task_completed(ticker)
                self.total_processed += 1
            elif current_state.has_error():
                self._mark_task_failed(ticker)
                self.total_errors += 1
            
            return current_state
            
        except Exception as e:
            self._mark_task_failed(ticker)
            self.total_errors += 1
            # Create error state if processing failed completely
            error_state = ProcessingState(
                ticker=ticker,
                original_file_path=file_path,
                status=ProcessingStatus.ERROR,
                error_message=f"Orchestrator error: {str(e)}"
            )
            # Save error state
            save_ref = self.state_manager.save_state.remote(error_state)
            ray.get(save_ref)
            return error_state
    
    def _execute_workflow_steps(self, initial_state: ProcessingState) -> ProcessingState:
        """
        Execute all workflow steps sequentially.
        
        Args:
            initial_state (ProcessingState): Starting state
            
        Returns:
            ProcessingState: Final state after all steps
        """
        current_state = initial_state
        
        # Step 1: Move to processing
        if current_state.status == ProcessingStatus.DISCOVERED:
            step_ref = self.processing_pool.process_step.remote(
                current_state, 
                MoveToProcessingStep(self.config.get('processing_dir', 'input/processing')))
            current_state = ray.get(step_ref)
            
            # Save state after each step
            save_ref = self.state_manager.save_state.remote(current_state)
            ray.get(save_ref)
            
            if current_state.has_error():
                return current_state
        
        # Step 2: Download SEC filing
        if current_state.status == ProcessingStatus.MOVED_TO_PROCESSING:
            step_ref = self.processing_pool.process_step.remote(
                current_state, 
                DownloadSecFilingStep(self.config.get('sec_filings_dir', 'sec-edgar-filings')))
            current_state = ray.get(step_ref)
            
            # Save state
            save_ref = self.state_manager.save_state.remote(current_state)
            ray.get(save_ref)
            
            if current_state.has_error():
                return current_state
        
        # Step 3: Extract facts
        if current_state.status == ProcessingStatus.SEC_FILING_DOWNLOADED:
            step_ref = self.processing_pool.process_step.remote(
                current_state,
                ExtractFactsStep())
            current_state = ray.get(step_ref)
            
            # Save state
            save_ref = self.state_manager.save_state.remote(current_state)
            ray.get(save_ref)
            
            if current_state.has_error():
                return current_state
        
        # Step 4: Save parquet
        if current_state.status == ProcessingStatus.FACTS_EXTRACTED:
            step_ref = self.processing_pool.process_step.remote(
                current_state, 
                SaveParquetStep(self.config.get('output_dir', 'output'))
            )
            current_state = ray.get(step_ref)
            
            # Save final state
            save_ref = self.state_manager.save_state.remote(current_state)
            ray.get(save_ref)
        
        return current_state
    
    def _mark_task_completed(self, ticker: str):
        """Mark a task as completed and clean up."""
        if ticker in self.active_tasks:
            del self.active_tasks[ticker]
        if ticker not in self.completed_tasks:
            self.completed_tasks.append(ticker)
    
    def _mark_task_failed(self, ticker: str):
        """Mark a task as failed and clean up."""
        if ticker in self.active_tasks:
            del self.active_tasks[ticker]
        if ticker not in self.failed_tasks:
            self.failed_tasks.append(ticker)
    
    def wait_for_completion(self, tickers: List[str], timeout: Optional[float] = None) -> Dict[str, ProcessingState]:
        """
        Wait for completion of multiple ticker processing tasks.
        
        Args:
            tickers (List[str]): List of ticker symbols to wait for
            timeout (Optional[float]): Timeout in seconds
            
        Returns:
            Dict[str, ProcessingState]: Final states for each ticker
        """
        # Get task references for the specified tickers
        task_refs = []
        ticker_to_ref = {}
        
        for ticker in tickers:
            if ticker in self.active_tasks:
                ref = self.active_tasks[ticker]
                task_refs.append(ref)
                ticker_to_ref[ref] = ticker
        
        if not task_refs:
            return {}
        
        # Wait for completion
        try:
            results = ray.get(task_refs, timeout=timeout)
            return {ticker_to_ref[ref]: result for ref, result in zip(task_refs, results)}
        except ray.exceptions.GetTimeoutError:
            # Return partial results for completed tasks
            ready_refs, remaining_refs = ray.wait(task_refs, num_returns=len(task_refs), timeout=0)
            if ready_refs:
                ready_results = ray.get(ready_refs)
                return {ticker_to_ref[ref]: result for ref, result in zip(ready_refs, ready_results)}
            return {}
    
    def retry_failed_processing(self, ticker: str) -> ray.ObjectRef:
        """
        Retry processing for a failed ticker.
        
        Args:
            ticker (str): Ticker symbol to retry
            
        Returns:
            ray.ObjectRef: Future containing the final processing state
        """
        # Remove from failed tasks if present
        if ticker in self.failed_tasks:
            self.failed_tasks.remove(ticker)
        
        # Get existing state
        existing_state_ref = self.state_manager.find_state_by_ticker.remote(ticker)
        existing_state = ray.get(existing_state_ref)
        
        if existing_state and existing_state.has_error():
            # Reset error and restart processing
            reset_ref = self.processing_pool.process_step.remote(existing_state, ResetErrorStep())
            reset_state = ray.get(reset_ref)
            
            # Start new processing task
            task = self._execute_workflow.remote(reset_state.original_file_path, ticker)
            self.active_tasks[ticker] = task
            return task
        
        return None
    
    @ray.method
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all processing activities.
        
        Returns:
            Dict[str, Any]: Complete processing status
        """
        # Get state manager stats
        state_stats_ref = self.state_manager.get_processing_stats.remote()
        state_stats = ray.get(state_stats_ref)
        
        # Get worker pool stats
        worker_stats = ray.get(self.processing_pool.get_pool_stats.remote())
        
        orchestrator_stats = self.get_orchestrator_stats()
        
        return {
            'orchestrator': orchestrator_stats,
            'state_manager': state_stats,
            'workers': worker_stats
        }
    
    def cleanup_resources(self) -> Dict[str, int]:
        """
        Clean up resources and return cleanup statistics.
        
        Returns:
            Dict[str, int]: Cleanup statistics
        """
        # Clean up state manager cache
        cache_cleaned_ref = self.state_manager.cleanup_cache.remote()
        cache_cleaned = ray.get(cache_cleaned_ref)
        
        # Clean up old completed states (keep 7 days)
        files_cleaned_ref = self.state_manager.cleanup_completed_states.remote(7)
        files_cleaned = ray.get(files_cleaned_ref)
        
        return {
            'cache_entries_cleaned': cache_cleaned,
            'state_files_cleaned': files_cleaned
        }
    
    @ray.method
    def shutdown(self):
        """Shutdown the orchestrator and all managed actors."""
        # Shutdown processing pool
        ray.get(self.processing_pool.shutdown.remote())
        
        # Kill actors
        ray.kill(self.processing_pool)
        ray.kill(self.state_manager)