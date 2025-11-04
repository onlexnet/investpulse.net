import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
import shutil
from datetime import datetime, timedelta

from src.state_manager import StateManager
from src.processing_state import ProcessingState, ProcessingStatus


class TestStateManager(unittest.TestCase):
    """Test cases for StateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "states")
        self.state_manager = StateManager(self.state_dir)
        
        self.ticker = 'AAPL'
        self.original_file_path = os.path.join(self.temp_dir, f"{self.ticker.lower()}.json")
        
        # Create test state
        self.test_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_creates_directory(self):
        """Test that StateManager creates the state directory on initialization."""
        new_dir = os.path.join(self.temp_dir, "new_states")
        self.assertFalse(os.path.exists(new_dir))
        
        new_manager = StateManager(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_save_state_creates_file(self):
        """Test that save_state creates a state file."""
        state_path = self.state_manager.save_state(self.test_state)
        
        self.assertTrue(os.path.exists(state_path))
        self.assertEqual(state_path, self.test_state.state_file_path)
        
        # Verify the file content
        with open(state_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['ticker'], self.ticker)
        self.assertEqual(data['original_file_path'], self.original_file_path)

    def test_save_state_with_existing_path(self):
        """Test saving state when state_file_path is already set."""
        existing_path = os.path.join(self.state_dir, "custom_state.json")
        self.test_state.state_file_path = existing_path
        
        saved_path = self.state_manager.save_state(self.test_state)
        
        self.assertEqual(saved_path, existing_path)
        self.assertTrue(os.path.exists(existing_path))

    def test_load_state_success(self):
        """Test loading state from an existing file."""
        # First save a state
        state_path = self.state_manager.save_state(self.test_state)
        
        # Then load it
        loaded_state = self.state_manager.load_state(state_path)
        
        self.assertEqual(loaded_state.ticker, self.test_state.ticker)
        self.assertEqual(loaded_state.original_file_path, self.test_state.original_file_path)
        self.assertEqual(loaded_state.state_file_path, state_path)

    def test_load_state_file_not_found(self):
        """Test loading state from non-existent file raises FileNotFoundError."""
        non_existent_path = os.path.join(self.state_dir, "nonexistent.json")
        
        with self.assertRaises(FileNotFoundError):
            self.state_manager.load_state(non_existent_path)

    def test_load_state_invalid_json(self):
        """Test loading state from file with invalid JSON."""
        invalid_json_path = os.path.join(self.state_dir, "invalid.json")
        os.makedirs(os.path.dirname(invalid_json_path), exist_ok=True)
        
        with open(invalid_json_path, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(json.JSONDecodeError):
            self.state_manager.load_state(invalid_json_path)

    def test_find_state_by_ticker_exists(self):
        """Test finding existing state by ticker."""
        # Save a state first
        self.state_manager.save_state(self.test_state)
        
        # Find it by ticker
        found_state = self.state_manager.find_state_by_ticker(self.ticker)
        
        self.assertIsNotNone(found_state)
        self.assertEqual(found_state.ticker, self.ticker)

    def test_find_state_by_ticker_not_exists(self):
        """Test finding non-existent state by ticker returns None."""
        found_state = self.state_manager.find_state_by_ticker("NONEXISTENT")
        self.assertIsNone(found_state)

    def test_list_states_empty(self):
        """Test listing states when directory is empty."""
        states = self.state_manager.list_states()
        self.assertEqual(len(states), 0)

    def test_list_states_with_multiple_states(self):
        """Test listing multiple states."""
        # Create and save multiple states
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        for ticker in tickers:
            state = ProcessingState(
                ticker=ticker,
                original_file_path=f"/test/{ticker.lower()}.json"
            )
            self.state_manager.save_state(state)
        
        states = self.state_manager.list_states()
        self.assertEqual(len(states), len(tickers))
        
        found_tickers = [state.ticker for state in states]
        for ticker in tickers:
            self.assertIn(ticker, found_tickers)

    def test_list_states_with_status_filter(self):
        """Test listing states with status filter."""
        # Create states with different statuses
        states_data = [
            ('AAPL', ProcessingStatus.DISCOVERED),
            ('MSFT', ProcessingStatus.COMPLETED),
            ('GOOGL', ProcessingStatus.ERROR)
        ]
        
        for ticker, status in states_data:
            state = ProcessingState(
                ticker=ticker,
                original_file_path=f"/test/{ticker.lower()}.json",
                status=status
            )
            self.state_manager.save_state(state)
        
        # Filter by COMPLETED status
        completed_states = self.state_manager.list_states(ProcessingStatus.COMPLETED)
        self.assertEqual(len(completed_states), 1)
        self.assertEqual(completed_states[0].ticker, 'MSFT')

    def test_list_states_ignores_corrupted_files(self):
        """Test that list_states ignores corrupted state files."""
        # Create a valid state
        self.state_manager.save_state(self.test_state)
        
        # Create a corrupted state file
        corrupted_path = os.path.join(self.state_dir, "corrupted_state.json")
        with open(corrupted_path, 'w') as f:
            f.write("invalid json")
        
        # list_states should only return the valid state
        states = self.state_manager.list_states()
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].ticker, self.ticker)

    @patch('src.state_manager.move_to_processing')
    def test_process_step_success(self, mock_processing_func):
        """Test successful process step execution."""
        # Mock the processing function to return an updated state
        updated_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.MOVED_TO_PROCESSING
        )
        mock_processing_func.return_value = updated_state
        
        result_state = self.state_manager.process_step(
            self.test_state, 
            mock_processing_func,
            "test_arg"
        )
        
        # Verify the processing function was called correctly
        mock_processing_func.assert_called_once_with(self.test_state, "test_arg")
        
        # Verify the result
        self.assertEqual(result_state.status, ProcessingStatus.MOVED_TO_PROCESSING)
        
        # Verify state was saved
        self.assertIsNotNone(result_state.state_file_path)
        self.assertTrue(os.path.exists(result_state.state_file_path))

    @patch('src.state_manager.handle_error')
    @patch('src.state_manager.move_to_processing')
    def test_process_step_handles_exception(self, mock_processing_func, mock_handle_error):
        """Test that process_step handles exceptions properly."""
        # Mock the processing function to raise an exception
        mock_processing_func.side_effect = Exception("Test error")
        
        # Mock handle_error to return an error state
        error_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.ERROR,
            error_message="Unexpected error in processing: Test error"
        )
        mock_handle_error.return_value = error_state
        
        result_state = self.state_manager.process_step(
            self.test_state, 
            mock_processing_func
        )
        
        # Verify error handling was called
        mock_handle_error.assert_called_once_with(
            self.test_state, 
            "Unexpected error in processing: Test error"
        )
        
        # Verify the error state was returned
        self.assertEqual(result_state.status, ProcessingStatus.ERROR)

    @patch('src.state_manager.StateManager.process_step')
    def test_execute_workflow_complete_flow(self, mock_process_step):
        """Test executing complete workflow from start to finish."""
        # Mock process_step to simulate successful progression through all steps
        step_states = [
            ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path, 
                          status=ProcessingStatus.MOVED_TO_PROCESSING),
            ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path, 
                          status=ProcessingStatus.SEC_FILING_DOWNLOADED),
            ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path, 
                          status=ProcessingStatus.FACTS_EXTRACTED),
            ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path, 
                          status=ProcessingStatus.COMPLETED)
        ]
        
        mock_process_step.side_effect = step_states
        
        config = {
            'processing_dir': 'test_processing',
            'sec_filings_dir': 'test_sec',
            'output_dir': 'test_output'
        }
        
        result_state = self.state_manager.execute_workflow(self.test_state, config)
        
        # Verify all steps were called
        self.assertEqual(mock_process_step.call_count, 4)
        
        # Verify final state
        self.assertEqual(result_state.status, ProcessingStatus.COMPLETED)

    @patch('src.state_manager.StateManager.process_step')
    def test_execute_workflow_stops_on_error(self, mock_process_step):
        """Test that workflow stops when a step encounters an error."""
        # Mock first step to return an error state
        error_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.ERROR,
            error_message="Test error"
        )
        error_state.has_error = MagicMock(return_value=True)
        mock_process_step.return_value = error_state
        
        config = {'processing_dir': 'test_processing'}
        
        result_state = self.state_manager.execute_workflow(self.test_state, config)
        
        # Verify only first step was called
        self.assertEqual(mock_process_step.call_count, 1)
        
        # Verify error state was returned
        self.assertEqual(result_state.status, ProcessingStatus.ERROR)

    @patch('src.state_manager.StateManager.execute_workflow')
    @patch('src.processing_functions.reset_error')
    def test_retry_failed_processing_success(self, mock_reset_error, mock_execute_workflow):
        """Test successful retry of failed processing."""
        # Create a failed state and save it
        failed_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.ERROR,
            error_message="Previous error"
        )
        failed_state.has_error = MagicMock(return_value=True)
        self.state_manager.save_state(failed_state)
        
        # Mock reset_error to return a reset state
        reset_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.DISCOVERED
        )
        mock_reset_error.return_value = reset_state
        
        # Mock execute_workflow to return completed state
        completed_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.COMPLETED
        )
        mock_execute_workflow.return_value = completed_state
        
        config = {'processing_dir': 'test'}
        
        result_state = self.state_manager.retry_failed_processing(self.ticker, config)
        
        # Verify reset_error was called
        mock_reset_error.assert_called_once_with(failed_state)
        
        # Verify execute_workflow was called with reset state
        mock_execute_workflow.assert_called_once_with(reset_state, config)
        
        # Verify result
        self.assertEqual(result_state.status, ProcessingStatus.COMPLETED)

    def test_retry_failed_processing_not_found(self):
        """Test retry when ticker state doesn't exist."""
        result = self.state_manager.retry_failed_processing("NONEXISTENT", {})
        self.assertIsNone(result)

    def test_retry_failed_processing_no_error(self):
        """Test retry when state has no error."""
        # Create a completed state
        completed_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.COMPLETED
        )
        completed_state.has_error = MagicMock(return_value=False)
        self.state_manager.save_state(completed_state)
        
        result = self.state_manager.retry_failed_processing(self.ticker, {})
        
        # Should return the existing state without processing
        self.assertEqual(result.status, ProcessingStatus.COMPLETED)

    def test_cleanup_completed_states(self):
        """Test cleanup of old completed states."""
        # Create states with different ages and statuses
        old_date = datetime.now() - timedelta(days=35)
        recent_date = datetime.now() - timedelta(days=10)
        
        states_data = [
            ('AAPL', ProcessingStatus.COMPLETED, old_date),
            ('MSFT', ProcessingStatus.COMPLETED, recent_date),
            ('GOOGL', ProcessingStatus.ERROR, old_date),  # Should not be removed
            ('TSLA', ProcessingStatus.COMPLETED, old_date)
        ]
        
        for ticker, status, updated_at in states_data:
            state = ProcessingState(
                ticker=ticker,
                original_file_path=f"/test/{ticker.lower()}.json",
                status=status,
                updated_at=updated_at
            )
            self.state_manager.save_state(state)
        
        # Run cleanup with 30 day retention
        removed_count = self.state_manager.cleanup_completed_states(keep_days=30)
        
        # Should remove 2 old completed states (AAPL, TSLA)
        self.assertEqual(removed_count, 2)
        
        # Verify remaining states
        remaining_states = self.state_manager.list_states()
        remaining_tickers = [state.ticker for state in remaining_states]
        
        self.assertIn('MSFT', remaining_tickers)  # Recent completed
        self.assertIn('GOOGL', remaining_tickers)  # Old but error status
        self.assertNotIn('AAPL', remaining_tickers)  # Old completed, removed
        self.assertNotIn('TSLA', remaining_tickers)  # Old completed, removed

    def test_workflow_resume_from_middle_step(self):
        """Test workflow can resume from any step."""
        # Create state in middle of workflow
        partial_state = ProcessingState(
            ticker=self.ticker,
            original_file_path=self.original_file_path,
            status=ProcessingStatus.SEC_FILING_DOWNLOADED
        )
        
        with patch('src.state_manager.StateManager.process_step') as mock_process_step:
            # Mock remaining steps
            step_states = [
                ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path,
                              status=ProcessingStatus.FACTS_EXTRACTED),
                ProcessingState(ticker=self.ticker, original_file_path=self.original_file_path,
                              status=ProcessingStatus.COMPLETED)
            ]
            mock_process_step.side_effect = step_states
            
            config = {'output_dir': 'test_output'}
            
            result_state = self.state_manager.execute_workflow(partial_state, config)
            
            # Should only call the remaining 2 steps
            self.assertEqual(mock_process_step.call_count, 2)
            self.assertEqual(result_state.status, ProcessingStatus.COMPLETED)


if __name__ == '__main__':
    unittest.main()
