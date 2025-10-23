import os
from typing import Any
from src.file_watcher import watch_input_folder
from src.sec_edgar_downloader import download_sec_filings
from src.fact_extractor import extract_top_facts, save_facts_to_parquet
from src.logger import setup_logger
from src.processing_state import ProcessingState, ProcessingStatus

INPUT_DIR = "input/entry"
OUTPUT_DIR = "output"
LOG_FILE = "app.log"

logger = setup_logger("app", LOG_FILE)

def process_ticker(processing_state: ProcessingState) -> None:
    """
    Process a ticker using ProcessingState: download SEC filing, extract facts, save to Parquet.

    Args:
        processing_state (ProcessingState): The processing state object to track progress.
    """
    try:
        logger.info(f"Processing ticker: {processing_state.ticker}")
        
        # Update status to downloading SEC filing
        processing_state.update_status(ProcessingStatus.DOWNLOADING_SEC_FILING)
        processing_state.save_to_file()
        
        # Download SEC filing
        filing_path = download_sec_filings(processing_state.ticker, OUTPUT_DIR)
        logger.info(f"Downloaded filing to: {filing_path}")
        
        # Update state with SEC filing path
        processing_state.set_sec_filing_path(filing_path)
        processing_state.save_to_file()
        
        # Extract facts
        processing_state.update_status(ProcessingStatus.EXTRACTING_FACTS)
        processing_state.save_to_file()
        
        facts = extract_top_facts(filing_path)
        logger.info(f"Extracted facts: {facts}")
        
        processing_state.update_status(ProcessingStatus.FACTS_EXTRACTED)
        processing_state.metadata['facts_count'] = len(facts) if facts else 0
        processing_state.save_to_file()
        
        # Save to Parquet
        processing_state.update_status(ProcessingStatus.SAVING_PARQUET)
        processing_state.save_to_file()
        
        parquet_path = save_facts_to_parquet(processing_state.ticker, facts, OUTPUT_DIR)
        logger.info(f"Saved facts to: {parquet_path}")
        
        # Mark as completed
        processing_state.set_parquet_output_path(parquet_path)
        processing_state.save_to_file()
        
        duration = processing_state.get_processing_duration()
        logger.info(f"Processing completed for {processing_state.ticker} in {duration:.2f} seconds")
        
    except Exception as e:
        error_msg = f"Error processing ticker {processing_state.ticker}: {e}"
        logger.error(error_msg)
        
        # Update state with error
        processing_state.update_status(ProcessingStatus.ERROR, str(e))
        processing_state.save_to_file()
        
        raise

if __name__ == "__main__":
    watch_input_folder(INPUT_DIR, process_ticker)
