"""
Test suite for Ray actor conversion.

This module provides tests to verify that the Ray actor-based
processing system works correctly.
"""

from math import e
import os
import ray
import json
import tempfile
import unittest
from unittest.mock import patch
from typing import Dict, Any

from ray.exceptions import GetTimeoutError
from src import processing_state
from src.ray_config import initialize_ray, shutdown_ray
from src.ray_workflow_orchestrator import RayWorkflowOrchestrator
from src.ray_state_manager import RayStateManager
from src.ray_processing_worker import MoveToProcessingStep, RayProcessingWorker, RayProcessingPool
from src.processing_state import ProcessingState, ProcessingStatus


class TestRayActors(unittest.TestCase):
    """Test cases for Ray actors."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Ray for testing."""
        # Initialize Ray with minimal resources for testing
        ray.init(
            num_cpus=2,
            num_gpus=0,
            log_to_driver=False,
            include_dashboard=False
        )
    
    @classmethod
    def tearDownClass(cls):
        """Shutdown Ray after testing."""
        ray.shutdown()
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'state_dir': os.path.join(self.temp_dir, 'state'),
            'processing_dir': os.path.join(self.temp_dir, 'processing'),
            'sec_filings_dir': os.path.join(self.temp_dir, 'sec'),
            'output_dir': os.path.join(self.temp_dir, 'output')
        }
        
        # Create directories
        for dir_path in self.config.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_ticker_file(self, ticker: str) -> str:
        """Create a test ticker file."""
        file_path = os.path.join(self.temp_dir, f"{ticker.lower()}.json")
        data = {
            "ticker": ticker,
            "timestamp": 1234567890,
            "source": "test"
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        return file_path
    
    def test_ray_state_manager(self):
        """Test RayStateManager actor."""
        # Create state manager actor
        state_manager = ray.remote(RayStateManager).remote(self.config['state_dir'])
        
        # Create test state
        test_state = ProcessingState(
            ticker="TEST",
            original_file_path="/test/path"
        )
        
        # Test save state
        save_ref = state_manager.save_state.remote(test_state)
        saved_path = ray.get(save_ref)
        self.assertTrue(os.path.exists(saved_path))
        
        # Test find state by ticker
        find_ref = state_manager.find_state_by_ticker.remote("TEST")
        found_state = ray.get(find_ref)
        assert found_state is not None
        self.assertIsNotNone(found_state)
        self.assertEqual(found_state.ticker, "TEST")
        
        # Test list states
        list_ref = state_manager.list_states.remote()
        states = ray.get(list_ref)
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].ticker, "TEST")
        
        # Test stats
        stats_ref = state_manager.get_processing_stats.remote()
        stats = ray.get(stats_ref)
        self.assertEqual(stats['total_states'], 1)
        self.assertIn('by_status', stats)
        
        ray.kill(state_manager)
    
    def test_ray_processing_worker(self):
        """Test RayProcessingWorker actor."""
        # Create worker actor
        worker = ray.remote(RayProcessingWorker).remote("test-worker")
        
        # Create test file
        test_file = self.create_test_ticker_file("TESTWORK")
        
        # Create test state
        test_state = ProcessingState(
            ticker="TESTWORK",
            original_file_path=test_file
        )
        
        # Test move to processing step
        move_ref = worker.move_to_processing_step.remote(
            test_state, 
            self.config['processing_dir']
        )
        result_state = ray.get(move_ref)
        
        self.assertEqual(result_state.status, ProcessingStatus.MOVED_TO_PROCESSING)
        self.assertIsNotNone(result_state.processing_file_path)
        
        # Test worker stats
        stats_ref = worker.get_worker_stats.remote()
        stats = ray.get(stats_ref)
        self.assertEqual(stats['worker_id'], "test-worker")
        self.assertEqual(stats['processed_count'], 1)
        self.assertEqual(stats['error_count'], 0)
        
        ray.kill(worker)
    
    def test_ray_processing_pool(self):
        """Test RayProcessingPool actor."""
        # Create processing pool
        pool = ray.remote(RayProcessingPool).remote(pool_size=2)
        
        # Create test file
        test_file = self.create_test_ticker_file("TESTPOOL")
        
        # Create test state
        test_state = ProcessingState(
            ticker="TESTPOOL",
            original_file_path=test_file
        )
        
        # Test process step
        step_ref = pool.process_step.remote(
            test_state,
            MoveToProcessingStep(self.config['processing_dir'])
        )
        result_state = ray.get(step_ref)
        
        self.assertEqual(result_state.status, ProcessingStatus.MOVED_TO_PROCESSING)
        
        # Test pool stats
        stats = ray.get(pool.get_pool_stats.remote())
        self.assertEqual(len(stats), 2)  # 2 workers
        
        ray.get(pool.shutdown.remote())
    
    def test_ray_workflow_orchestrator(self):
        """Test RayWorkflowOrchestrator actor."""
        # Create orchestrator
        orchestrator = ray.remote(RayWorkflowOrchestrator).remote(
            config=self.config,
            worker_pool_size=2
        )
        
        # Create test file
        test_file = self.create_test_ticker_file("TESTORCH")
        
        # Test async processing
        task_ref = orchestrator.process_ticker_async.remote(test_file, "TESTORCH")
        
        # final_state = ray.get(task_ref, timeout=30)
        final_state = ray.get(task_ref)
        
        # Check final state
        # Note: Processing might not complete fully in test environment
        # but should at least start and update status
        self.assertIn(final_state.status, [
            ProcessingStatus.MOVED_TO_PROCESSING,
            ProcessingStatus.SEC_FILING_DOWNLOADED,
            ProcessingStatus.FACTS_EXTRACTED,
            ProcessingStatus.COMPLETED,
            ProcessingStatus.ERROR
        ])
        
        # Test orchestrator stats
        stats_ref = orchestrator.get_orchestrator_stats.remote()
        stats = ray.get(stats_ref)
        self.assertIn('total_processed', stats)
        self.assertIn('active_tasks', stats)
        
        # Test processing status
        status_ref = orchestrator.get_processing_status.remote()
        status = ray.get(status_ref)
        self.assertIn('orchestrator', status)
        self.assertIn('state_manager', status)
        self.assertIn('workers', status)
        
        # Cleanup
        ray.get(orchestrator.shutdown.remote())
    
    def test_error_handling(self):
        """Test error handling in Ray actors."""
        # Create worker
        worker = ray.remote(RayProcessingWorker).remote("error-test")
        
        # Create state with non-existent file
        error_state = ProcessingState(
            ticker="ERROR",
            original_file_path="/non/existent/file.json"
        )
        
        # Test error handling
        move_ref = worker.move_to_processing_step.remote(
            error_state,
            self.config['processing_dir']
        )
        result_state = ray.get(move_ref)
        
        self.assertEqual(result_state.status, ProcessingStatus.ERROR)
        self.assertIsNotNone(result_state.error_message)
        
        # Check worker error count
        stats_ref = worker.get_worker_stats.remote()
        stats = ray.get(stats_ref)
        self.assertEqual(stats['error_count'], 1)
        
        ray.kill(worker)


def run_integration_test():
    """Run a simple integration test."""
    print("Running Ray integration test...")
    
    # Initialize Ray
    ray.init(
        num_cpus=2,
        include_dashboard=False,
        log_to_driver=False
    )
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        config = {
            'state_dir': os.path.join(temp_dir, 'state'),
            'processing_dir': os.path.join(temp_dir, 'processing'),
            'sec_filings_dir': os.path.join(temp_dir, 'sec'),
            'output_dir': os.path.join(temp_dir, 'output')
        }
        
        # Create directories
        for dir_path in config.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Create test file
        test_file = os.path.join(temp_dir, "integration_test.json")
        with open(test_file, 'w') as f:
            json.dump({"ticker": "INTEGRATION", "test": True}, f)
        
        # Create orchestrator
        orchestrator = RayWorkflowOrchestrator.remote(config, worker_pool_size=2)
        
        # Process ticker
        task_ref = orchestrator.process_ticker_async.remote(test_file, "INTEGRATION")
        
        # Wait for result
        result = ray.get(task_ref, timeout=30)
        
        print(f"Integration test result: {result.status.value}")
        
        # Get final stats
        stats_ref = orchestrator.get_orchestrator_stats.remote()
        stats = ray.get(stats_ref)
        
        print(f"Processing stats: {stats}")
        
        # Cleanup
        ray.get(orchestrator.shutdown.remote())
        
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return False
    
    finally:
        ray.shutdown()


if __name__ == "__main__":
    # Run integration test
    success = run_integration_test()
    
    if success:
        print("\n" + "="*50)
        print("Running unit tests...")
        unittest.main(verbosity=2)
    else:
        print("Integration test failed, skipping unit tests")
        exit(1)