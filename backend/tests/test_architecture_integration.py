"""
Integration test for the new processing architecture.

This test verifies that the complete workflow works end-to-end.
"""

import os
import tempfile
import json
import unittest
from src.processing_state import ProcessingState, ProcessingStatus
from src.state_manager import StateManager


class TestArchitectureIntegration(unittest.TestCase):
    """Integration tests for the new architecture."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.ticker = "TEST"
        
        # Create test input file
        self.input_file = os.path.join(self.temp_dir, "test.json")
        with open(self.input_file, 'w') as f:
            json.dump({'ticker': self.ticker}, f)
        
        # Setup directories
        self.state_dir = os.path.join(self.temp_dir, "state")
        self.processing_dir = os.path.join(self.temp_dir, "processing") 
        self.sec_dir = os.path.join(self.temp_dir, "sec")
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        self.config = {
            'state_dir': self.state_dir,
            'processing_dir': self.processing_dir,
            'sec_filings_dir': self.sec_dir,
            'output_dir': self.output_dir
        }
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete processing workflow from start to finish."""
        # Initialize state manager
        state_manager = StateManager(self.state_dir)
        
        # Create initial state
        initial_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.input_file
        )
        
        # Execute workflow
        final_state = state_manager.execute_workflow(initial_state, self.config)
        
        # Verify final state
        self.assertEqual(final_state.status, ProcessingStatus.COMPLETED)
        self.assertIsNotNone(final_state.parquet_output_path)
        self.assertTrue(os.path.exists(final_state.parquet_output_path))
        
        # Verify state was saved
        saved_state = state_manager.find_state_by_ticker(self.ticker)
        self.assertIsNotNone(saved_state)
        self.assertEqual(saved_state.status, ProcessingStatus.COMPLETED)
    
    def test_state_persistence(self):
        """Test that states are properly saved and loaded."""
        state_manager = StateManager(self.state_dir)
        
        # Create and save a state
        test_state = ProcessingState(
            ticker="PERSIST",
            original_file_path="/test/path.json",
            status=ProcessingStatus.EXTRACTING_FACTS
        )
        
        saved_path = state_manager.save_state(test_state)
        self.assertTrue(os.path.exists(saved_path))
        
        # Load it back
        loaded_state = state_manager.load_state(saved_path)
        self.assertEqual(loaded_state.ticker, test_state.ticker)
        self.assertEqual(loaded_state.status, test_state.status)
        self.assertEqual(loaded_state.original_file_path, test_state.original_file_path)
    
    def test_error_handling_and_retry(self):
        """Test error handling and retry functionality."""
        state_manager = StateManager(self.state_dir)
        
        # Create a state that will fail (non-existent file)
        failing_state = ProcessingState(
            ticker="FAIL",
            original_file_path="/non/existent/file.json"
        )
        
        # Execute workflow (should fail)
        final_state = state_manager.execute_workflow(failing_state, self.config)
        
        # Verify it failed
        self.assertEqual(final_state.status, ProcessingStatus.ERROR)
        self.assertIsNotNone(final_state.error_message)
        
        # Verify the failed state was saved
        failed_state = state_manager.find_state_by_ticker("FAIL")
        self.assertIsNotNone(failed_state)
        self.assertEqual(failed_state.status, ProcessingStatus.ERROR)
        
        # Test that we can create a successful workflow from scratch
        success_file = os.path.join(self.temp_dir, "success.json")
        with open(success_file, 'w') as f:
            json.dump({'ticker': 'SUCCESS'}, f)
        
        success_state = ProcessingState(
            ticker="SUCCESS",
            original_file_path=success_file
        )
        
        success_result = state_manager.execute_workflow(success_state, self.config)
        self.assertEqual(success_result.status, ProcessingStatus.COMPLETED)


if __name__ == '__main__':
    unittest.main()