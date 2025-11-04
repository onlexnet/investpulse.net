"""
Processing functions for ticker file processing workflow.

This module contains pure functions that take a ProcessingState as input
and return a modified ProcessingState as output. Each function handles
one specific step in the processing pipeline.
"""

import os
import shutil
from datetime import datetime
from typing import Optional
from dataclasses import replace

from .processing_state import ProcessingState, ProcessingStatus


def move_to_processing(state: ProcessingState, processing_dir: str) -> ProcessingState:
    """
    Move file to processing directory and update state.
    
    This function moves the ticker file from its original location to the
    processing directory and updates the state accordingly.
    
    Args:
        state (ProcessingState): Current processing state
        processing_dir (str): Directory to move the file to
        
    Returns:
        ProcessingState: Updated state with new file path and status
    """
    if not os.path.exists(state.original_file_path):
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message=f"Original file not found: {state.original_file_path}",
            updated_at=datetime.now()
        )
    
    try:
        # Ensure processing directory exists
        os.makedirs(processing_dir, exist_ok=True)
        
        # Generate new file path
        filename = os.path.basename(state.original_file_path)
        new_path = os.path.join(processing_dir, filename)
        
        # Move the file
        shutil.move(state.original_file_path, new_path)
        
        # Return updated state
        return replace(
            state,
            processing_file_path=new_path,
            status=ProcessingStatus.MOVED_TO_PROCESSING,
            updated_at=datetime.now()
        )
        
    except OSError as e:
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message=f"Failed to move file: {str(e)}",
            updated_at=datetime.now()
        )


def download_sec_filing(state: ProcessingState, output_dir: str) -> ProcessingState:
    """
    Download SEC filing and update state.
    
    This function downloads the SEC filing for the ticker and updates the
    state with the downloaded filing path.
    
    Args:
        state (ProcessingState): Current processing state
        output_dir (str): Directory to save the SEC filing
        
    Returns:
        ProcessingState: Updated state with SEC filing path
    """
    # Update status to indicate download is starting
    state_downloading = replace(
        state,
        status=ProcessingStatus.DOWNLOADING_SEC_FILING,
        updated_at=datetime.now()
    )
    
    try:
        # Create output directory structure
        ticker_dir = os.path.join(output_dir, state.ticker.upper())
        filing_dir = os.path.join(ticker_dir, "10-Q")
        os.makedirs(filing_dir, exist_ok=True)
        
        # Generate SEC filing path
        sec_filing_path = os.path.join(filing_dir, "full-submission.txt")
        
        # TODO: Implement actual SEC filing download logic
        # For now, simulate download by creating a placeholder file
        with open(sec_filing_path, 'w') as f:
            f.write(f"SEC filing for {state.ticker}")
        
        return replace(
            state,
            sec_filing_path=sec_filing_path,
            status=ProcessingStatus.SEC_FILING_DOWNLOADED,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message=f"Failed to download SEC filing: {str(e)}",
            updated_at=datetime.now()
        )


def extract_facts(state: ProcessingState) -> ProcessingState:
    """
    Extract facts from SEC filing and update state.
    
    This function processes the downloaded SEC filing to extract financial
    facts and data points.
    
    Args:
        state (ProcessingState): Current processing state
        
    Returns:
        ProcessingState: Updated state after fact extraction
    """
    if not state.sec_filing_path or not os.path.exists(state.sec_filing_path):
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message="SEC filing not found for fact extraction",
            updated_at=datetime.now()
        )
    
    try:
        # Update status to indicate extraction is starting
        state_extracting = replace(
            state,
            status=ProcessingStatus.EXTRACTING_FACTS,
            updated_at=datetime.now()
        )
        
        # TODO: Implement actual fact extraction logic
        # For now, simulate extraction by updating metadata
        
        # Update metadata with extracted facts
        updated_metadata = {**state.metadata, 'facts_extracted': True}
        
        return replace(
            state,
            metadata=updated_metadata,
            status=ProcessingStatus.FACTS_EXTRACTED,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message=f"Failed to extract facts: {str(e)}",
            updated_at=datetime.now()
        )


def save_parquet(state: ProcessingState, output_dir: str) -> ProcessingState:
    """
    Save processed data to parquet format and update state.
    
    This function saves the extracted facts and processed data to a parquet
    file for efficient storage and analysis.
    
    Args:
        state (ProcessingState): Current processing state
        output_dir (str): Directory to save the parquet file
        
    Returns:
        ProcessingState: Updated state with parquet output path
    """
    try:
        # Update status to indicate saving is starting
        state_saving = replace(
            state,
            status=ProcessingStatus.SAVING_PARQUET,
            updated_at=datetime.now()
        )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        parquet_path = os.path.join(output_dir, f"{state.ticker}_data.parquet")
        
        # TODO: Implement actual parquet saving logic
        # For now, simulate parquet creation
        with open(parquet_path, 'w') as f:
            f.write(f"Parquet data for {state.ticker}")
        
        return replace(
            state,
            parquet_output_path=parquet_path,
            status=ProcessingStatus.COMPLETED,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        return replace(
            state,
            status=ProcessingStatus.ERROR,
            error_message=f"Failed to save parquet: {str(e)}",
            updated_at=datetime.now()
        )


def handle_error(state: ProcessingState, error_message: str) -> ProcessingState:
    """
    Handle error state and update accordingly.
    
    This function creates an error state with the provided error message
    and appropriate timestamps.
    
    Args:
        state (ProcessingState): Current processing state
        error_message (str): Error message to set
        
    Returns:
        ProcessingState: Updated state with error status
    """
    return replace(
        state,
        status=ProcessingStatus.ERROR,
        error_message=error_message,
        updated_at=datetime.now()
    )


def reset_error(state: ProcessingState) -> ProcessingState:
    """
    Reset error state to allow retry of processing.
    
    This function clears the error message and resets the status to allow
    processing to be retried from the appropriate step.
    
    Args:
        state (ProcessingState): Current processing state with error
        
    Returns:
        ProcessingState: Updated state with cleared error
    """
    if not state.has_error():
        return state
    
    # Determine appropriate status to reset to based on completed steps
    if state.parquet_output_path:
        new_status = ProcessingStatus.FACTS_EXTRACTED
    elif state.sec_filing_path:
        new_status = ProcessingStatus.SEC_FILING_DOWNLOADED
    elif state.processing_file_path:
        new_status = ProcessingStatus.MOVED_TO_PROCESSING
    else:
        new_status = ProcessingStatus.DISCOVERED
    
    return replace(
        state,
        status=new_status,
        error_message=None,
        updated_at=datetime.now()
    )
