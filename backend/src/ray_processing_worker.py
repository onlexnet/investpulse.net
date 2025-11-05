"""
Ray actor for processing individual workflow steps.

This module provides the RayProcessingWorker actor that handles individual
processing steps like downloading SEC filings, extracting facts, etc.
"""

from dataclasses import dataclass
import ray, ray.actor as actor
from typing import Dict, Any
from datetime import datetime

from .processing_state import ProcessingState, ProcessingStatus
from .processing_functions import (
    move_to_processing,
    download_sec_filing,
    extract_facts,
    save_parquet,
    handle_error,
    reset_error
)


class RayProcessingWorker:
    """
    Ray actor for executing individual processing steps.
    
    This actor handles the execution of processing functions in a distributed
    manner, allowing for parallel processing of different tickers or steps.
    """
    
    def __init__(self, worker_id: str):
        """
        Initialize the processing worker.
        
        Args:
            worker_id (str): Unique identifier for this worker
        """
        self.worker_id = worker_id
        self.processed_count = 0
        self.error_count = 0
        
    @ray.method
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this worker.
        
        Returns:
            Dict[str, Any]: Worker statistics
        """
        return {
            'worker_id': self.worker_id,
            'processed_count': self.processed_count,
            'error_count': self.error_count
        }
    
    @ray.method
    def move_to_processing_step(self, state: ProcessingState, processing_dir: str) -> ProcessingState:
        """
        Execute the move to processing step.
        
        Args:
            state (ProcessingState): Current processing state
            processing_dir (str): Directory to move file to
            
        Returns:
            ProcessingState: Updated state after processing
        """
        try:
            result_state = move_to_processing(state, processing_dir)
            if result_state.has_error():
                self.error_count += 1
            else:
                self.processed_count += 1
            return result_state
        except Exception as e:
            self.error_count += 1
            return handle_error(state, f"Worker {self.worker_id} - Move to processing failed: {str(e)}")
    
    @ray.method
    def download_sec_filing_step(self, state: ProcessingState, output_dir: str) -> ProcessingState:
        """
        Execute the SEC filing download step.
        
        Args:
            state (ProcessingState): Current processing state
            output_dir (str): Directory to save SEC filing
            
        Returns:
            ProcessingState: Updated state after processing
        """
        try:
            result_state = download_sec_filing(state, output_dir)
            if result_state.has_error():
                self.error_count += 1
            else:
                self.processed_count += 1
            return result_state
        except Exception as e:
            self.error_count += 1
            return handle_error(state, f"Worker {self.worker_id} - SEC filing download failed: {str(e)}")
    
    @ray.method
    def extract_facts_step(self, state: ProcessingState) -> ProcessingState:
        """
        Execute the facts extraction step.
        
        Args:
            state (ProcessingState): Current processing state
            
        Returns:
            ProcessingState: Updated state after processing
        """
        try:
            result_state = extract_facts(state)
            if result_state.has_error():
                self.error_count += 1
            else:
                self.processed_count += 1
            return result_state
        except Exception as e:
            self.error_count += 1
            return handle_error(state, f"Worker {self.worker_id} - Facts extraction failed: {str(e)}")
    
    @ray.method
    def save_parquet_step(self, state: ProcessingState, output_dir: str) -> ProcessingState:
        """
        Execute the parquet saving step.
        
        Args:
            state (ProcessingState): Current processing state
            output_dir (str): Directory to save parquet file
            
        Returns:
            ProcessingState: Updated state after processing
        """
        try:
            result_state = save_parquet(state, output_dir)
            if result_state.has_error():
                self.error_count += 1
            else:
                self.processed_count += 1
            return result_state
        except Exception as e:
            self.error_count += 1
            return handle_error(state, f"Worker {self.worker_id} - Parquet saving failed: {str(e)}")
    
    @ray.method
    def reset_error_step(self, state: ProcessingState) -> ProcessingState:
        """
        Reset error state to allow retry.
        
        Args:
            state (ProcessingState): Current processing state with error
            
        Returns:
            ProcessingState: Updated state with cleared error
        """
        return reset_error(state)

@dataclass
class MoveToProcessingStep:
    processing_dir: str

@dataclass
class DownloadSecFilingStep:
    output_dir: str

@dataclass
class ExtractFactsStep:
    pass

@dataclass
class SaveParquetStep:
    output_dir: str

@dataclass
class ResetErrorStep:
    pass

WorkerStep = MoveToProcessingStep | DownloadSecFilingStep | ExtractFactsStep | SaveParquetStep | ResetErrorStep

class RayProcessingPool:
    """
    Ray actor that manages a pool of processing workers.
    
    This actor coordinates multiple workers and distributes tasks among them
    for optimal resource utilization.
    """
    
    def __init__(self, pool_size: int = 4):
        """
        Initialize the processing pool.
        
        Args:
            pool_size (int): Number of workers in the pool
        """
        self.pool_size = pool_size
        self.workers: list[actor.ActorProxy[RayProcessingWorker]] = []
        self.current_worker_index = 0
        
        # Create worker actors
        for i in range(pool_size):
            worker = ray.remote(RayProcessingWorker).remote(f"worker-{i}")
            self.workers.append(worker)
    
    def _get_next_worker(self) -> actor.ActorProxy[RayProcessingWorker]:
        """
        Get the next available worker using round-robin scheduling.
        
        Returns:
            ray.ObjectRef: Reference to the next worker
        """
        worker = self.workers[self.current_worker_index]
        self.current_worker_index = (self.current_worker_index + 1) % self.pool_size
        return worker
    
    @ray.method
    def get_pool_stats(self) -> list[Any]:
        """
        Get statistics for all workers in the pool.
        
        Returns:
            ray.ObjectRef: Future containing list of worker statistics
        """
        stats_futures = [worker.get_worker_stats.remote() for worker in self.workers]
        return ray.get(stats_futures)
    
    @ray.method
    def process_step(self, state: ProcessingState, worker_step: WorkerStep) -> ProcessingState:
        """
        Process a step using the next available worker.
        
        Args:
            step_name (str): Name of the processing step
            state (ProcessingState): Current processing state
            *args: Additional arguments for the processing function
            **kwargs: Additional keyword arguments for the processing function
            
        Returns:
            ray.ObjectRef: Future containing updated state
        """
        worker = self._get_next_worker()
        match worker_step:
            case MoveToProcessingStep(processing_dir):
                result_ref = worker.move_to_processing_step.remote(state, processing_dir)
            case DownloadSecFilingStep(output_dir):
                result_ref = worker.download_sec_filing_step.remote(state, output_dir)
            case ExtractFactsStep():
                result_ref = worker.extract_facts_step.remote(state)
            case SaveParquetStep(output_dir):
                result_ref = worker.save_parquet_step.remote(state, output_dir)
            case ResetErrorStep():
                result_ref = worker.reset_error_step.remote(state)

        return ray.get(result_ref)
    
    @ray.method
    def shutdown(self):
        """Shutdown all workers in the pool."""
        for worker in self.workers:
            ray.kill(worker)
        self.workers.clear()