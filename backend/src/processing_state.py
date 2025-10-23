"""
Processing state management for ticker file processing workflow.

This module provides the ProcessingState class that tracks the entire lifecycle
of processing a ticker file from discovery to final parquet output.
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


class ProcessingStatus(Enum):
    """Status enum for different stages of processing."""
    DISCOVERED = "discovered"
    MOVED_TO_PROCESSING = "moved_to_processing"
    DOWNLOADING_SEC_FILING = "downloading_sec_filing"
    SEC_FILING_DOWNLOADED = "sec_filing_downloaded"
    EXTRACTING_FACTS = "extracting_facts"
    FACTS_EXTRACTED = "facts_extracted"
    SAVING_PARQUET = "saving_parquet"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProcessingState:
    """
    Represents the state of processing for a ticker file.
    
    This class tracks the entire workflow from file discovery to parquet output,
    including timestamps, file paths, and any errors that occur.
    
    Attributes:
        ticker (str): The ticker symbol being processed
        original_file_path (str): Path to the original input JSON file
        processing_file_path (Optional[str]): Path to the file in processing folder
        state_file_path (Optional[str]): Path to the state JSON file
        status (ProcessingStatus): Current processing status
        created_at (datetime): When processing started
        updated_at (datetime): When state was last updated
        sec_filing_path (Optional[str]): Path to downloaded SEC filing
        parquet_output_path (Optional[str]): Path to final parquet file
        error_message (Optional[str]): Error message if processing failed
        metadata (Dict[str, Any]): Additional metadata for the processing
    """
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
    
    def __post_init__(self) -> None:
        """Initialize timestamps and metadata if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.metadata is None:
            self.metadata = {}
    
    def update_status(self, status: ProcessingStatus, 
                     error_message: Optional[str] = None) -> None:
        """
        Update the processing status and timestamp.
        
        Args:
            status (ProcessingStatus): New status to set
            error_message (Optional[str]): Error message if status is ERROR
        """
        self.status = status
        self.updated_at = datetime.now()
        if error_message:
            self.error_message = error_message
    
    def set_sec_filing_path(self, path: str) -> None:
        """
        Set the SEC filing path and update status.
        
        Args:
            path (str): Path to the downloaded SEC filing
        """
        self.sec_filing_path = path
        self.update_status(ProcessingStatus.SEC_FILING_DOWNLOADED)
    
    def set_parquet_output_path(self, path: str) -> None:
        """
        Set the parquet output path and mark as completed.
        
        Args:
            path (str): Path to the final parquet file
        """
        self.parquet_output_path = path
        self.update_status(ProcessingStatus.COMPLETED)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ProcessingState to dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the state
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        # Convert enum to string value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingState':
        """
        Create ProcessingState from dictionary (JSON deserialization).
        
        Args:
            data (Dict[str, Any]): Dictionary representation of the state
            
        Returns:
            ProcessingState: Reconstructed ProcessingState object
        """
        # Convert ISO format strings back to datetime objects
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert string status back to enum
        if 'status' in data:
            data['status'] = ProcessingStatus(data['status'])
        
        return cls(**data)
    
    def save_to_file(self, file_path: Optional[str] = None) -> str:
        """
        Save the current state to a JSON file.
        
        Args:
            file_path (Optional[str]): Path to save the state file. 
                                     If None, uses self.state_file_path
        
        Returns:
            str: Path where the state was saved
            
        Raises:
            ValueError: If no file path is provided and state_file_path is None
        """
        if file_path is None:
            if self.state_file_path is None:
                raise ValueError("No file path provided and state_file_path is None")
            file_path = self.state_file_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        if self.state_file_path is None:
            self.state_file_path = file_path
            
        return file_path
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProcessingState':
        """
        Load ProcessingState from a JSON file.
        
        Args:
            file_path (str): Path to the state JSON file
            
        Returns:
            ProcessingState: Loaded ProcessingState object
            
        Raises:
            FileNotFoundError: If the state file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        state = cls.from_dict(data)
        state.state_file_path = file_path
        return state
    
    def is_completed(self) -> bool:
        """
        Check if processing is completed successfully.
        
        Returns:
            bool: True if status is COMPLETED, False otherwise
        """
        return self.status == ProcessingStatus.COMPLETED
    
    def has_error(self) -> bool:
        """
        Check if processing encountered an error.
        
        Returns:
            bool: True if status is ERROR, False otherwise
        """
        return self.status == ProcessingStatus.ERROR
    
    def get_processing_duration(self) -> Optional[float]:
        """
        Get the total processing duration in seconds.
        
        Returns:
            Optional[float]: Duration in seconds if processing is complete or errored,
                           None if still in progress
        """
        if self.status in [ProcessingStatus.COMPLETED, ProcessingStatus.ERROR]:
            return (self.updated_at - self.created_at).total_seconds()
        return None
