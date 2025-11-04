"""
Unit tests for processing functions.

Tests cover individual processing functions to ensure they work correctly
with the pure data model.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from dataclasses import replace

from src.processing_state import ProcessingState, ProcessingStatus
from src.processing_functions import (
    move_to_processing,
    download_sec_filing,
    extract_facts,
    save_parquet,
    handle_error,
    reset_error
)


class TestProcessingFunctions(unittest.TestCase):
    """Test cases for processing functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ticker = "AAPL"
        self.temp_dir = tempfile.mkdtemp()
        self.original_file_path = os.path.join(self.temp_dir, "aapl.json")
        
        # Create a test input file
        with open(self.original_file_path, 'w') as f:
            json.dump({'ticker': self.ticker}, f)
        
        self.state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_move_to_processing_success(self):
        """Test successful file move to processing directory."""
        processing_dir = os.path.join(self.temp_dir, "processing")
        
        result_state = move_to_processing(self.state, processing_dir)
        
        # Check that status was updated
        self.assertEqual(result_state.status, ProcessingStatus.MOVED_TO_PROCESSING)
        
        # Check that file was moved
        self.assertIsNotNone(result_state.processing_file_path)
        self.assertTrue(os.path.exists(result_state.processing_file_path))
        self.assertFalse(os.path.exists(self.original_file_path))
        
        # Check that updated_at was set
        self.assertIsNotNone(result_state.updated_at)
        self.assertGreater(result_state.updated_at, self.state.updated_at)
    
    def test_download_sec_filing_success(self):
        """Test successful SEC filing download."""
        # Set up state as if file was already moved
        moved_state = replace(
            self.state,
            status=ProcessingStatus.MOVED_TO_PROCESSING,
            processing_file_path=os.path.join(self.temp_dir, "aapl.json")
        )
        
        output_dir = os.path.join(self.temp_dir, "sec-filings")
        
        result_state = download_sec_filing(moved_state, output_dir)
        
        # Check that status was updated
        self.assertEqual(result_state.status, ProcessingStatus.SEC_FILING_DOWNLOADED)
        
        # Check that SEC filing path was set
        self.assertIsNotNone(result_state.sec_filing_path)
        self.assertTrue(os.path.exists(result_state.sec_filing_path))
    
    def test_extract_facts_success(self):
        """Test successful fact extraction."""
        # Create a mock SEC filing
        sec_filing_path = os.path.join(self.temp_dir, "filing.txt")
        with open(sec_filing_path, 'w') as f:
            f.write("Mock SEC filing content")
        
        # Set up state as if SEC filing was downloaded
        download_state = replace(
            self.state,
            status=ProcessingStatus.SEC_FILING_DOWNLOADED,
            sec_filing_path=sec_filing_path
        )
        
        result_state = extract_facts(download_state)
        
        # Check that status was updated
        self.assertEqual(result_state.status, ProcessingStatus.FACTS_EXTRACTED)
        
        # Check that metadata was updated
        self.assertIn('facts_extracted', result_state.metadata)
        self.assertTrue(result_state.metadata['facts_extracted'])
    
    def test_save_parquet_success(self):
        """Test successful parquet saving."""
        # Set up state as if facts were extracted
        facts_state = replace(
            self.state,
            status=ProcessingStatus.FACTS_EXTRACTED,
            metadata={'facts_extracted': True}
        )
        
        output_dir = os.path.join(self.temp_dir, "output")
        
        result_state = save_parquet(facts_state, output_dir)
        
        # Check that status was updated
        self.assertEqual(result_state.status, ProcessingStatus.COMPLETED)
        
        # Check that parquet path was set
        self.assertIsNotNone(result_state.parquet_output_path)
        self.assertTrue(os.path.exists(result_state.parquet_output_path))
    
    def test_handle_error(self):
        """Test error handling function."""
        error_message = "Test error occurred"
        
        result_state = handle_error(self.state, error_message)
        
        # Check that error status was set
        self.assertEqual(result_state.status, ProcessingStatus.ERROR)
        self.assertEqual(result_state.error_message, error_message)
        self.assertIsNotNone(result_state.updated_at)
    
    def test_reset_error_basic(self):
        """Test basic error reset functionality."""
        # Create an error state
        error_state = replace(
            self.state,
            status=ProcessingStatus.ERROR,
            error_message="Test error"
        )
        
        result_state = reset_error(error_state)
        
        # Check that error was cleared
        self.assertNotEqual(result_state.status, ProcessingStatus.ERROR)
        self.assertIsNone(result_state.error_message)
        self.assertEqual(result_state.status, ProcessingStatus.DISCOVERED)


if __name__ == '__main__':
    unittest.main()
