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

if __name__ == '__main__':
    unittest.main()
