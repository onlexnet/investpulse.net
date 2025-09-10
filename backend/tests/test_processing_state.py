"""
Unit tests for ProcessingState class.

Tests cover state management, serialization, file operations, and edge cases.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import patch, mock_open

from src.processing_state import ProcessingState, ProcessingStatus


class TestProcessingState(unittest.TestCase):
    """Test cases for ProcessingState class."""

    def setUp(self):
        """Set up test fixtures."""
        self.ticker = "AAPL"
        self.original_file_path = "/test/input/aapl.json"
        
    def test_initialization_with_defaults(self):
        """Test ProcessingState initialization with default values."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        self.assertEqual(state.ticker, self.ticker)
        self.assertEqual(state.original_file_path, self.original_file_path)
        self.assertEqual(state.status, ProcessingStatus.DISCOVERED)
        self.assertIsNone(state.processing_file_path)
        self.assertIsNone(state.state_file_path)
        self.assertIsNone(state.sec_filing_path)
        self.assertIsNone(state.parquet_output_path)
        self.assertIsNone(state.error_message)
        self.assertIsInstance(state.created_at, datetime)
        self.assertIsInstance(state.updated_at, datetime)
        self.assertEqual(state.metadata, {})

    def test_initialization_with_custom_values(self):
        """Test ProcessingState initialization with custom values."""
        created_time = datetime(2025, 1, 1, 12, 0, 0)
        updated_time = datetime(2025, 1, 1, 12, 5, 0)
        metadata = {"test": "value"}
        
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.DOWNLOADING_SEC_FILING,
            created_at=created_time,
            updated_at=updated_time,
            metadata=metadata
        )
        
        self.assertEqual(state.status, ProcessingStatus.DOWNLOADING_SEC_FILING)
        self.assertEqual(state.created_at, created_time)
        self.assertEqual(state.updated_at, updated_time)
        self.assertEqual(state.metadata, metadata)

    def test_update_status(self):
        """Test status update functionality."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        old_updated_at = state.updated_at
        
        # Update status without error
        state.update_status(ProcessingStatus.DOWNLOADING_SEC_FILING)
        
        self.assertEqual(state.status, ProcessingStatus.DOWNLOADING_SEC_FILING)
        self.assertGreater(state.updated_at, old_updated_at)
        self.assertIsNone(state.error_message)
        
        # Update status with error
        error_msg = "Test error message"
        state.update_status(ProcessingStatus.ERROR, error_msg)
        
        self.assertEqual(state.status, ProcessingStatus.ERROR)
        self.assertEqual(state.error_message, error_msg)

    def test_set_sec_filing_path(self):
        """Test setting SEC filing path."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        filing_path = "/test/sec-filings/AAPL/10-Q/filing.txt"
        state.set_sec_filing_path(filing_path)
        
        self.assertEqual(state.sec_filing_path, filing_path)
        self.assertEqual(state.status, ProcessingStatus.SEC_FILING_DOWNLOADED)

    def test_set_parquet_output_path(self):
        """Test setting parquet output path."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        parquet_path = "/test/output/AAPL_facts.parquet"
        state.set_parquet_output_path(parquet_path)
        
        self.assertEqual(state.parquet_output_path, parquet_path)
        self.assertEqual(state.status, ProcessingStatus.COMPLETED)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        created_time = datetime(2025, 1, 1, 12, 0, 0)
        updated_time = datetime(2025, 1, 1, 12, 5, 0)
        metadata = {"facts_count": 10}
        
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            processing_file_path="/test/processing/aapl.json",
            state_file_path="/test/processing/aapl.state.json",
            status=ProcessingStatus.COMPLETED,
            created_at=created_time,
            updated_at=updated_time,
            sec_filing_path="/test/sec-filings/AAPL/filing.txt",
            parquet_output_path="/test/output/AAPL_facts.parquet",
            metadata=metadata
        )
        
        result = state.to_dict()
        
        self.assertEqual(result['ticker'], self.ticker)
        self.assertEqual(result['original_file_path'], self.original_file_path)
        self.assertEqual(result['status'], ProcessingStatus.COMPLETED.value)
        self.assertEqual(result['created_at'], created_time.isoformat())
        self.assertEqual(result['updated_at'], updated_time.isoformat())
        self.assertEqual(result['metadata'], metadata)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'ticker': self.ticker,
            'original_file_path': self.original_file_path,
            'processing_file_path': '/test/processing/aapl.json',
            'state_file_path': '/test/processing/aapl.state.json',
            'status': ProcessingStatus.COMPLETED.value,
            'created_at': '2025-01-01T12:00:00',
            'updated_at': '2025-01-01T12:05:00',
            'sec_filing_path': '/test/sec-filings/AAPL/filing.txt',
            'parquet_output_path': '/test/output/AAPL_facts.parquet',
            'error_message': None,
            'metadata': {'facts_count': 10}
        }
        
        state = ProcessingState.from_dict(data)
        
        self.assertEqual(state.ticker, self.ticker)
        self.assertEqual(state.original_file_path, self.original_file_path)
        self.assertEqual(state.status, ProcessingStatus.COMPLETED)
        self.assertEqual(state.created_at, datetime(2025, 1, 1, 12, 0, 0))
        self.assertEqual(state.updated_at, datetime(2025, 1, 1, 12, 5, 0))
        self.assertEqual(state.metadata['facts_count'], 10)

    def test_save_to_file(self):
        """Test saving state to file."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file_path = os.path.join(temp_dir, "test_state.json")
            
            # Save to file
            saved_path = state.save_to_file(state_file_path)
            
            self.assertEqual(saved_path, state_file_path)
            self.assertEqual(state.state_file_path, state_file_path)
            self.assertTrue(os.path.exists(state_file_path))
            
            # Verify file contents
            with open(state_file_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['ticker'], self.ticker)
            self.assertEqual(data['status'], ProcessingStatus.DISCOVERED.value)

    def test_save_to_file_with_existing_state_file_path(self):
        """Test saving when state_file_path is already set."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file_path = os.path.join(temp_dir, "existing_state.json")
            state.state_file_path = state_file_path
            
            # Save without providing path
            saved_path = state.save_to_file()
            
            self.assertEqual(saved_path, state_file_path)
            self.assertTrue(os.path.exists(state_file_path))

    def test_save_to_file_no_path_error(self):
        """Test save_to_file raises error when no path provided."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        with self.assertRaises(ValueError) as cm:
            state.save_to_file()
        
        self.assertIn("No file path provided", str(cm.exception))

    def test_load_from_file(self):
        """Test loading state from file."""
        # First create a state and save it
        original_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.COMPLETED
        )
        original_state.set_parquet_output_path("/test/output/AAPL.parquet")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file_path = os.path.join(temp_dir, "load_test.json")
            original_state.save_to_file(state_file_path)
            
            # Load the state
            loaded_state = ProcessingState.load_from_file(state_file_path)
            
            self.assertEqual(loaded_state.ticker, original_state.ticker)
            self.assertEqual(loaded_state.status, original_state.status)
            self.assertEqual(loaded_state.parquet_output_path, original_state.parquet_output_path)
            self.assertEqual(loaded_state.state_file_path, state_file_path)

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            ProcessingState.load_from_file("/non/existent/file.json")

    def test_is_completed(self):
        """Test is_completed method."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        # Initially not completed
        self.assertFalse(state.is_completed())
        
        # Set to completed
        state.update_status(ProcessingStatus.COMPLETED)
        self.assertTrue(state.is_completed())
        
        # Set to error
        state.update_status(ProcessingStatus.ERROR)
        self.assertFalse(state.is_completed())

    def test_has_error(self):
        """Test has_error method."""
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
        # Initially no error
        self.assertFalse(state.has_error())
        
        # Set to error
        state.update_status(ProcessingStatus.ERROR, "Test error")
        self.assertTrue(state.has_error())
        
        # Set to completed
        state.update_status(ProcessingStatus.COMPLETED)
        self.assertFalse(state.has_error())

    def test_get_processing_duration(self):
        """Test get_processing_duration method."""
        created_time = datetime(2025, 1, 1, 12, 0, 0)
        
        state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            created_at=created_time
        )
        
        # In progress - should return None
        self.assertIsNone(state.get_processing_duration())
        
        # Completed - should return duration
        completed_time = datetime(2025, 1, 1, 12, 5, 30)  # 5.5 minutes later
        state.status = ProcessingStatus.COMPLETED
        state.updated_at = completed_time
        
        duration = state.get_processing_duration()
        self.assertEqual(duration, 330.0)  # 5.5 minutes = 330 seconds
        
        # Error - should also return duration
        state.status = ProcessingStatus.ERROR
        duration = state.get_processing_duration()
        self.assertEqual(duration, 330.0)

    def test_roundtrip_serialization(self):
        """Test full roundtrip serialization/deserialization."""
        # Create a complex state
        original_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            processing_file_path="/test/processing/aapl.json",
            status=ProcessingStatus.FACTS_EXTRACTED,
            metadata={"facts_count": 15, "processing_notes": "Test run"}
        )
        original_state.set_sec_filing_path("/test/sec-filings/AAPL/filing.txt")
        
        # Convert to dict and back
        state_dict = original_state.to_dict()
        restored_state = ProcessingState.from_dict(state_dict)
        
        # Verify all fields match
        self.assertEqual(restored_state.ticker, original_state.ticker)
        self.assertEqual(restored_state.original_file_path, original_state.original_file_path)
        self.assertEqual(restored_state.processing_file_path, original_state.processing_file_path)
        self.assertEqual(restored_state.status, original_state.status)
        self.assertEqual(restored_state.sec_filing_path, original_state.sec_filing_path)
        self.assertEqual(restored_state.metadata, original_state.metadata)
        self.assertEqual(restored_state.created_at, original_state.created_at)
        self.assertEqual(restored_state.updated_at, original_state.updated_at)


if __name__ == '__main__':
    unittest.main()
