import os
import ray
import signal
import sys
from typing import Any, Dict
from src.file_watcher import watch_input_folder
from src.sec_edgar_downloader import download_sec_filings
from src.fact_extractor import extract_top_facts, save_facts_to_parquet
from src.logger import setup_logger
from src.processing_state import ProcessingState, ProcessingStatus
from src.ray_config import initialize_ray, shutdown_ray, get_cluster_info, DEVELOPMENT_CONFIG
from src.ray_workflow_orchestrator import RayWorkflowOrchestrator

INPUT_DIR = "input/entry"
PROCESSING_DIR = "input/processing"
OUTPUT_DIR = "output"
SEC_FILINGS_DIR = "sec-edgar-filings"
LOG_FILE = "app.log"

logger = setup_logger("app", LOG_FILE)

# Configuration for processing
PROCESSING_CONFIG = {
    'state_dir': PROCESSING_DIR,
    'processing_dir': PROCESSING_DIR,
    'sec_filings_dir': SEC_FILINGS_DIR,
    'output_dir': OUTPUT_DIR
}

# Global Ray orchestrator
orchestrator = None


def setup_ray_environment():
    """
    Initialize Ray environment and create the workflow orchestrator.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    global orchestrator
    
    # Initialize Ray
    if not initialize_ray(DEVELOPMENT_CONFIG):
        logger.error("Failed to initialize Ray")
        return False
    
    # Log cluster information
    cluster_info = get_cluster_info()
    logger.info(f"Ray cluster info: {cluster_info}")
    
    # Create workflow orchestrator
    try:
        orchestrator = ray.remote(RayWorkflowOrchestrator).remote(
            config=PROCESSING_CONFIG,
            worker_pool_size=4
        )
        logger.info("Ray workflow orchestrator created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create workflow orchestrator: {e}")
        return False


def cleanup_ray_environment():
    """Clean up Ray environment gracefully."""
    global orchestrator
    
    if orchestrator:
        try:
            ray.get(orchestrator.shutdown.remote())
            logger.info("Workflow orchestrator shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down orchestrator: {e}")
        
        orchestrator = None
    
    shutdown_ray()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup_ray_environment()
    sys.exit(0)


def process_ticker_file(file_path: str, ticker: str) -> None:
    """
    Process a ticker file using Ray actors for distributed processing.

    Args:
        file_path (str): Path to the ticker JSON file
        ticker (str): Ticker symbol extracted from the file
    """
    global orchestrator
    
    if not orchestrator:
        logger.error("Orchestrator not initialized")
        return
    
    try:
        logger.info(f"Starting Ray-based processing for ticker: {ticker}")
        
        # Submit processing task to the orchestrator
        task_ref = orchestrator.process_ticker_async.remote(file_path, ticker)
        
        # Get the result (this will block until completion)
        final_state = ray.get(task_ref)
        
        # Log final results
        if final_state.is_completed():
            duration = final_state.get_processing_duration()
            logger.info(f"Processing completed for {ticker} in {duration:.2f} seconds")
            logger.info(f"Output file: {final_state.parquet_output_path}")
        elif final_state.has_error():
            logger.error(f"Processing failed for {ticker}: {final_state.error_message}")
        else:
            logger.warning(f"Processing incomplete for {ticker}, status: {final_state.status.value}")
        
    except Exception as e:
        error_msg = f"Unexpected error processing ticker {ticker}: {e}"
        logger.error(error_msg)
        raise


def get_processing_status() -> Dict[str, Any]:
    """
    Get comprehensive processing status from the orchestrator.
    
    Returns:
        Dict[str, Any]: Processing status information
    """
    global orchestrator
    
    if not orchestrator:
        return {'error': 'Orchestrator not initialized'}
    
    try:
        status_ref = orchestrator.get_processing_status.remote()
        return ray.get(status_ref)
    except Exception as e:
        return {'error': f'Failed to get processing status: {e}'}


def retry_failed_ticker(ticker: str) -> bool:
    """
    Retry processing for a failed ticker.
    
    Args:
        ticker (str): Ticker symbol to retry
        
    Returns:
        bool: True if retry was initiated successfully
    """
    global orchestrator
    
    if not orchestrator:
        logger.error("Orchestrator not initialized")
        return False
    
    try:
        retry_ref = orchestrator.retry_failed_processing.remote(ticker)
        if retry_ref:
            logger.info(f"Retry initiated for ticker: {ticker}")
            return True
        else:
            logger.warning(f"No failed state found for ticker: {ticker}")
            return False
    except Exception as e:
        logger.error(f"Failed to retry ticker {ticker}: {e}")
        return False


def cleanup_resources() -> Dict[str, int]:
    """
    Clean up processing resources and return statistics.
    
    Returns:
        Dict[str, int]: Cleanup statistics
    """
    global orchestrator
    
    if not orchestrator:
        return {'error': 'Orchestrator not initialized'}
    
    try:
        cleanup_ref = orchestrator.cleanup_resources.remote()
        return ray.get(cleanup_ref)
    except Exception as e:
        return {'error': f'Failed to cleanup resources: {e}'}


if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ensure required directories exist
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(PROCESSING_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SEC_FILINGS_DIR, exist_ok=True)
    
    logger.info("Starting Ray-based ticker file processing service...")
    logger.info(f"Watching directory: {INPUT_DIR}")
    logger.info(f"Processing directory: {PROCESSING_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    # Initialize Ray environment
    if not setup_ray_environment():
        logger.error("Failed to setup Ray environment, exiting...")
        sys.exit(1)
    
    try:
        # Start watching the input folder
        watch_input_folder(INPUT_DIR, process_ticker_file)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
    finally:
        cleanup_ray_environment()
