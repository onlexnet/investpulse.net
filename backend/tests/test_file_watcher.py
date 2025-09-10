import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from src.file_watcher import TickerFileHandler
from src.processing_state import ProcessingState, ProcessingStatus
from typing import Optional


class TestTickerFileHandler(unittest.TestCase):
    """Test cases for TickerFileHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = self.temp_dir
        self.processing_dir = os.path.join(self.input_dir, "processing")
        self.callback_called = False
        self.captured_state = None
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def callback_for_test(self, processing_state: ProcessingState) -> None:
        """Callback function to capture ProcessingState."""
        self.callback_called = True
        self.captured_state = processing_state

    def test_file_handler_initialization(self):
        """Test TickerFileHandler initialization creates processing directory."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        self.assertEqual(handler.input_dir, self.input_dir)
        self.assertEqual(handler.processing_dir, self.processing_dir)
        self.assertTrue(os.path.exists(self.processing_dir))

    def test_file_watcher_detects_ticker_and_moves_file(self):
        """Test that TickerFileHandler detects ticker, moves file, and creates state."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create a test JSON file
        test_file_path = os.path.join(self.input_dir, "aapl.json")
        with open(test_file_path, 'w') as f:
            json.dump({'ticker': 'AAPL'}, f)
        
        # Create mock event
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(test_file_path)
        handler.on_created(event)
        
        # Verify callback was called
        self.assertTrue(self.callback_called)
        self.assertIsNotNone(self.captured_state)
        
        # Verify ProcessingState details
        state = self.captured_state
        self.assertEqual(state.ticker, 'AAPL')
        self.assertEqual(state.original_file_path, test_file_path)
        self.assertEqual(state.status, ProcessingStatus.MOVED_TO_PROCESSING)
        
        # Verify file was moved
        self.assertFalse(os.path.exists(test_file_path))
        moved_file_path = os.path.join(self.processing_dir, "aapl.json")
        self.assertTrue(os.path.exists(moved_file_path))
        self.assertEqual(state.processing_file_path, moved_file_path)
        
        # Verify state file was created
        state_file_path = os.path.join(self.processing_dir, "aapl.state.json")
        self.assertTrue(os.path.exists(state_file_path))
        self.assertEqual(state.state_file_path, state_file_path)
        
        # Verify state file content
        with open(state_file_path, 'r') as f:
            state_data = json.load(f)
        
        self.assertEqual(state_data['ticker'], 'AAPL')
        self.assertEqual(state_data['status'], ProcessingStatus.MOVED_TO_PROCESSING.value)

    def test_file_handler_ignores_non_json_files(self):
        """Test that handler ignores non-JSON files."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create a non-JSON file
        test_file_path = os.path.join(self.input_dir, "test.txt")
        with open(test_file_path, 'w') as f:
            f.write("not json")
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(test_file_path)
        handler.on_created(event)
        
        # Verify callback was not called
        self.assertFalse(self.callback_called)
        
        # Verify file was not moved
        self.assertTrue(os.path.exists(test_file_path))

    def test_file_handler_ignores_directories(self):
        """Test that handler ignores directory creation events."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create a directory
        test_dir_path = os.path.join(self.input_dir, "test_dir")
        os.makedirs(test_dir_path)
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = True
        
        event = MockEvent(test_dir_path)
        handler.on_created(event)
        
        # Verify callback was not called
        self.assertFalse(self.callback_called)

    def test_file_handler_handles_missing_ticker(self):
        """Test handler behavior when JSON file has no ticker field."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create a JSON file without ticker
        test_file_path = os.path.join(self.input_dir, "no_ticker.json")
        with open(test_file_path, 'w') as f:
            json.dump({'symbol': 'AAPL'}, f)  # Wrong field name
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(test_file_path)
        
        with patch('logging.warning') as mock_warning:
            handler.on_created(event)
        
        # Verify warning was logged
        mock_warning.assert_called_once()
        
        # Verify callback was not called
        self.assertFalse(self.callback_called)
        
        # Verify file was not moved
        self.assertTrue(os.path.exists(test_file_path))

    @patch('logging.error')
    def test_file_handler_handles_invalid_json(self, mock_error):
        """Test handler behavior with invalid JSON file."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create an invalid JSON file
        test_file_path = os.path.join(self.input_dir, "invalid.json")
        with open(test_file_path, 'w') as f:
            f.write("{ invalid json")
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(test_file_path)
        handler.on_created(event)
        
        # Verify error was logged
        mock_error.assert_called_once()
        
        # Verify callback was not called
        self.assertFalse(self.callback_called)

    @patch('logging.error')
    def test_file_handler_handles_file_move_error(self, mock_error):
        """Test handler behavior when file move operation fails."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Create a test JSON file
        test_file_path = os.path.join(self.input_dir, "aapl.json")
        with open(test_file_path, 'w') as f:
            json.dump({'ticker': 'AAPL'}, f)
        
        class MockEvent:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = MockEvent(test_file_path)
        
        # Mock shutil.move to raise an exception
        with patch('shutil.move', side_effect=OSError("Permission denied")):
            handler.on_created(event)
        
        # Verify error was logged
        mock_error.assert_called()
        
        # Verify callback was not called
        self.assertFalse(self.callback_called)

    def test_state_file_naming_convention(self):
        """Test that state files follow the correct naming convention."""
        handler = TickerFileHandler(self.input_dir, self.callback_for_test)
        
        # Test with different file names
        test_cases = [
            ("aapl.json", "aapl.state.json"),
            ("tesla.json", "tesla.state.json"),
            ("microsoft_stock.json", "microsoft_stock.state.json")
        ]
        
        for input_filename, expected_state_filename in test_cases:
            # Reset callback state
            self.callback_called = False
            self.captured_state = None
            
            # Create test file
            test_file_path = os.path.join(self.input_dir, input_filename)
            with open(test_file_path, 'w') as f:
                json.dump({'ticker': 'TEST'}, f)
            
            class MockEvent:
                def __init__(self, src_path: str):
                    self.src_path = src_path
                    self.is_directory = False
            
            event = MockEvent(test_file_path)
            handler.on_created(event)
            
            # Verify state file name
            expected_state_path = os.path.join(self.processing_dir, expected_state_filename)
            self.assertEqual(self.captured_state.state_file_path, expected_state_path)
            self.assertTrue(os.path.exists(expected_state_path))


class DummyCallback:
    """
    Dummy callback to capture ticker symbol for testing (legacy compatibility).
    """
    def __init__(self):
        self.ticker: Optional[str] = None
    
    def __call__(self, ticker: str) -> None:
        self.ticker = ticker


def test_file_watcher_detects_ticker() -> None:
    """
    Legacy test function for backward compatibility.
    Test that TickerFileHandler detects ticker in a new JSON file.
    """
    # This test needs to be updated to work with the new ProcessingState approach
    # For now, we'll create a simple callback that extracts the ticker
    captured_ticker = None
    
    def simple_callback(processing_state: ProcessingState) -> None:
        nonlocal captured_ticker
        captured_ticker = processing_state.ticker
    
    with tempfile.TemporaryDirectory() as temp_dir:
        handler = TickerFileHandler(temp_dir, simple_callback)
        
        # Create test file
        test_file_path = os.path.join(temp_dir, "aapl.json")
        with open(test_file_path, 'w') as f:
            json.dump({'ticker': 'AAPL'}, f)
        
        class Event:
            def __init__(self, src_path: str):
                self.src_path = src_path
                self.is_directory = False
        
        event = Event(test_file_path)
        handler.on_created(event)
        
        assert captured_ticker == 'AAPL'


if __name__ == '__main__':
    unittest.main()
