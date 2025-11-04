import os
import json
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock
import pandas as pd

from src.app import INPUT_DIR, OUTPUT_DIR, process_ticker_file
from src.file_watcher import TickerFileHandler, watch_input_folder
from src.processing_state import ProcessingState, ProcessingStatus


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete app workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_input_dir = os.path.join(self.temp_dir, "input", "entry")
        self.test_output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.test_input_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        self.processing_states = []
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def callback_for_test(self, processing_state: ProcessingState) -> None:
        """Callback function to capture ProcessingState."""
        self.processing_states.append(processing_state)

    def test_input_entry_directory_structure(self):
        """Test that the app uses input/entry/ directory structure correctly."""
        # Verify the INPUT_DIR constant is set correctly
        self.assertEqual(INPUT_DIR, "input/entry")
        
        # Test file handler with input/entry structure
        handler = TickerFileHandler(self.test_input_dir, self.callback_for_test)
        
        # Verify processing directory is created under input/entry/
        expected_processing_dir = os.path.join(self.test_input_dir, "processing")
        self.assertEqual(handler.processing_dir, expected_processing_dir)
        self.assertTrue(os.path.exists(expected_processing_dir))

    def test_file_workflow_with_entry_directory(self):
        """Test complete file workflow using input/entry/ directory."""
        handler = TickerFileHandler(self.test_input_dir, self.callback_for_test)
        
        # Create a test ticker file in input/entry/
        ticker_file = os.path.join(self.test_input_dir, "aapl.json")
        with open(ticker_file, 'w') as f:
            json.dump({"ticker": "AAPL"}, f)
        
        # Simulate file creation event
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(ticker_file)
        handler.on_created(event)
        
        # Verify file was moved to input/entry/processing/
        processing_file = os.path.join(self.test_input_dir, "processing", "aapl.json")
        self.assertTrue(os.path.exists(processing_file))
        self.assertFalse(os.path.exists(ticker_file))
        
        # Verify state file was created in input/entry/processing/
        state_file = os.path.join(self.test_input_dir, "processing", "aapl.state.json")
        self.assertTrue(os.path.exists(state_file))
        
        # Verify processing state was captured
        self.assertEqual(len(self.processing_states), 1)
        state = self.processing_states[0]
        self.assertEqual(state.ticker, "AAPL")
        self.assertEqual(state.processing_file_path, processing_file)
        self.assertEqual(state.state_file_path, state_file)

    @patch('src.app.save_facts_to_parquet')
    @patch('src.app.extract_top_facts')
    @patch('src.app.download_sec_filings')
    def test_end_to_end_processing_workflow(self, mock_download, mock_extract, mock_save):
        """Test end-to-end processing workflow with input/entry/ structure."""
        # Mock return values
        filing_path = os.path.join(self.temp_dir, "sec-filings", "AAPL", "filing.txt")
        facts = [{"fact": f"fact_{i}", "value": f"value_{i}"} for i in range(10)]
        parquet_path = os.path.join(self.test_output_dir, "AAPL_facts.parquet")
        
        mock_download.return_value = filing_path
        mock_extract.return_value = facts
        mock_save.return_value = parquet_path
        
        # Create file handler and simulate file creation
        handler = TickerFileHandler(self.test_input_dir, process_ticker)
        
        ticker_file = os.path.join(self.test_input_dir, "msft.json")
        with open(ticker_file, 'w') as f:
            json.dump({"ticker": "MSFT"}, f)
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(ticker_file)
        handler.on_created(event)
        
        # Verify mocks were called
        mock_download.assert_called_once_with("MSFT", OUTPUT_DIR)
        mock_extract.assert_called_once_with(filing_path)
        mock_save.assert_called_once_with("MSFT", facts, OUTPUT_DIR)
        
        # Verify state file was updated with completion
        state_file = os.path.join(self.test_input_dir, "processing", "msft.state.json")
        self.assertTrue(os.path.exists(state_file))
        
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        self.assertEqual(state_data["status"], ProcessingStatus.COMPLETED.value)
        self.assertEqual(state_data["ticker"], "MSFT")

    def test_multiple_ticker_files_processing(self):
        """Test processing multiple ticker files in sequence."""
        handler = TickerFileHandler(self.test_input_dir, self.callback_for_test)
        
        tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        
        for ticker in tickers:
            ticker_file = os.path.join(self.test_input_dir, f"{ticker.lower()}.json")
            with open(ticker_file, 'w') as f:
                json.dump({"ticker": ticker}, f)
            
            class MockEvent:
                def __init__(self, src_path: str):
                    self.src_path = src_path
                    self.is_directory = False
            
            event = MockEvent(ticker_file)
            handler.on_created(event)
        
        # Verify all files were processed
        self.assertEqual(len(self.processing_states), len(tickers))
        
        for i, ticker in enumerate(tickers):
            state = self.processing_states[i]
            self.assertEqual(state.ticker, ticker)
            self.assertEqual(state.status, ProcessingStatus.MOVED_TO_PROCESSING)
            
            # Verify files were moved to processing directory
            processing_file = os.path.join(self.test_input_dir, "processing", f"{ticker.lower()}.json")
            self.assertTrue(os.path.exists(processing_file))
            
            # Verify state files were created
            state_file = os.path.join(self.test_input_dir, "processing", f"{ticker.lower()}.state.json")
            self.assertTrue(os.path.exists(state_file))

    def test_directory_structure_creation(self):
        """Test that required directory structures are created correctly."""
        # Test with a fresh temp directory
        fresh_temp_dir = tempfile.mkdtemp()
        try:
            fresh_input_dir = os.path.join(fresh_temp_dir, "input", "entry")
            
            # TickerFileHandler should create the processing directory
            handler = TickerFileHandler(fresh_input_dir, self.callback_for_test)
            
            # Verify processing directory was created
            processing_dir = os.path.join(fresh_input_dir, "processing")
            self.assertTrue(os.path.exists(processing_dir))
            
        finally:
            shutil.rmtree(fresh_temp_dir, ignore_errors=True)

    @patch('logging.error')
    def test_error_handling_in_integration(self, mock_logger_error):
        """Test error handling in the complete integration workflow."""
        # Create a handler that will trigger an error
        def error_callback(processing_state: ProcessingState):
            raise Exception("Test processing error")
        
        handler = TickerFileHandler(self.test_input_dir, error_callback)
        
        # Create a test file
        ticker_file = os.path.join(self.test_input_dir, "error_test.json")
        with open(ticker_file, 'w') as f:
            json.dump({"ticker": "ERROR"}, f)
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(ticker_file)
        handler.on_created(event)
        
        # Verify error was logged
        mock_logger_error.assert_called()
        
        # Verify file was still moved to processing (error occurred in callback)
        processing_file = os.path.join(self.test_input_dir, "processing", "error_test.json")
        self.assertTrue(os.path.exists(processing_file))


class TestAppConfiguration(unittest.TestCase):
    """Test app configuration and constants."""
    
    def test_input_dir_configuration(self):
        """Test that INPUT_DIR is configured correctly."""
        self.assertEqual(INPUT_DIR, "input/entry")
        
    def test_output_dir_configuration(self):
        """Test that OUTPUT_DIR is configured correctly."""
        self.assertEqual(OUTPUT_DIR, "output")

    def test_app_module_import(self):
        """Test that all required modules can be imported."""
        try:
            from src.app import process_ticker, INPUT_DIR, OUTPUT_DIR
            from src.file_watcher import watch_input_folder, TickerFileHandler
            from src.processing_state import ProcessingState, ProcessingStatus
            from src.sec_edgar_downloader import download_sec_filings
            from src.fact_extractor import extract_top_facts, save_facts_to_parquet
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")


if __name__ == '__main__':
    unittest.main()