"""
Tests for Path-based event handlers.

This module tests the new Path-based event handlers to ensure they work
correctly with pathlib.Path objects.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.path_event_handler import PathFileSystemEvent, PathEventHandlerAdapter
from src.path_file_watcher import PathTickerFileHandler
from watchdog.events import FileCreatedEvent


class TestPathEventHandler(unittest.TestCase):
    """Test cases for Path-based event handlers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test.json"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_path_file_system_event_creation(self):
        """Test creating PathFileSystemEvent from watchdog event."""
        # Create a mock watchdog event
        watchdog_event = FileCreatedEvent(str(self.test_file))
        
        # Convert to Path event
        path_event = PathFileSystemEvent.from_watchdog_event(watchdog_event)
        
        # Verify the conversion
        self.assertIsInstance(path_event.src_path, Path)
        self.assertEqual(path_event.src_path, self.test_file)
        self.assertEqual(path_event.event_type, "created")
        self.assertFalse(path_event.is_directory)
    
    def test_path_event_handler_adapter(self):
        """Test the adapter that bridges watchdog and Path handlers."""
        # Create a mock Path handler
        mock_path_handler = Mock()
        
        # Create the adapter
        adapter = PathEventHandlerAdapter(mock_path_handler)
        
        # Create a watchdog event
        watchdog_event = FileCreatedEvent(str(self.test_file))
        
        # Dispatch through the adapter
        adapter.dispatch(watchdog_event)
        
        # Verify the Path handler was called
        mock_path_handler.dispatch.assert_called_once()
        
        # Get the converted event
        call_args = mock_path_handler.dispatch.call_args[0]
        path_event = call_args[0]
        
        self.assertIsInstance(path_event, PathFileSystemEvent)
        self.assertIsInstance(path_event.src_path, Path)
        self.assertEqual(path_event.src_path, self.test_file)
    
    def test_path_ticker_file_handler(self):
        """Test the Path-based ticker file handler."""
        # Create a test JSON file
        test_data = {"ticker": "AAPL", "metadata": {"test": True}}
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create a mock callback
        mock_callback = Mock()
        
        # Create the handler
        handler = PathTickerFileHandler(self.temp_dir, mock_callback)
        
        # Create a Path event
        path_event = PathFileSystemEvent(src_path=self.test_file)
        path_event.event_type = "created"
        path_event.is_directory = False
        
        # Handle the event
        handler.on_created(path_event)
        
        # Verify callback was called with Path object
        mock_callback.assert_called_once_with(self.test_file, "AAPL")
        
        # Verify the first argument is a Path object
        call_args = mock_callback.call_args[0]
        self.assertIsInstance(call_args[0], Path)
    
    def test_path_handler_ignores_non_json_files(self):
        """Test that Path handler ignores non-JSON files."""
        # Create a non-JSON file
        text_file = self.temp_dir / "test.txt"
        text_file.write_text("This is not JSON")
        
        # Create a mock callback
        mock_callback = Mock()
        
        # Create the handler
        handler = PathTickerFileHandler(self.temp_dir, mock_callback)
        
        # Create a Path event for the text file
        path_event = PathFileSystemEvent(src_path=text_file)
        path_event.event_type = "created"
        path_event.is_directory = False
        
        # Handle the event
        handler.on_created(path_event)
        
        # Verify callback was not called
        mock_callback.assert_not_called()
    
    def test_path_handler_ignores_directories(self):
        """Test that Path handler ignores directory events."""
        # Create a directory
        test_dir = self.temp_dir / "subdir"
        test_dir.mkdir()
        
        # Create a mock callback
        mock_callback = Mock()
        
        # Create the handler
        handler = PathTickerFileHandler(self.temp_dir, mock_callback)
        
        # Create a Path event for the directory
        path_event = PathFileSystemEvent(src_path=test_dir)
        path_event.event_type = "created"
        path_event.is_directory = True
        
        # Handle the event
        handler.on_created(path_event)
        
        # Verify callback was not called
        mock_callback.assert_not_called()
    
    def test_path_benefits_demonstration(self):
        """Demonstrate the benefits of using Path objects."""
        # Create a nested directory structure
        nested_dir = self.temp_dir / "input" / "processing"
        nested_dir.mkdir(parents=True)
        
        test_file = nested_dir / "aapl.json"
        test_data = {"ticker": "AAPL"}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        def path_callback(file_path: Path, ticker: str) -> None:
            """Callback that demonstrates Path object benefits."""
            # Easy path manipulation
            self.assertEqual(file_path.name, "aapl.json")
            self.assertEqual(file_path.suffix, ".json") 
            self.assertEqual(file_path.stem, "aapl")
            self.assertEqual(file_path.parent.name, "processing")
            
            # Easy path operations
            self.assertTrue(file_path.exists())
            self.assertGreater(file_path.stat().st_size, 0)
            
            # Easy path construction
            state_file = file_path.with_suffix('.state.json')
            expected_state = nested_dir / "aapl.state.json"
            self.assertEqual(state_file, expected_state)
            
            # Cross-platform path handling
            relative_path = file_path.relative_to(self.temp_dir)
            expected_parts = ("input", "processing", "aapl.json")
            self.assertEqual(relative_path.parts, expected_parts)
        
        # Create handler and test
        handler = PathTickerFileHandler(nested_dir, path_callback)
        
        path_event = PathFileSystemEvent(src_path=test_file)
        path_event.event_type = "created"
        path_event.is_directory = False
        
        handler.on_created(path_event)


if __name__ == '__main__':
    unittest.main()