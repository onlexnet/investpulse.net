import os
from typing import Any
from src.file_watcher import watch_input_folder
from src.sec_edgar_downloader import download_sec_filings
from src.fact_extractor import extract_top_facts, save_facts_to_parquet
from src.logger import setup_logger

INPUT_DIR = "input"
OUTPUT_DIR = "output"
LOG_FILE = "app.log"

logger = setup_logger("app", LOG_FILE)

def process_ticker(ticker: str) -> None:
    """
    Process a ticker: download SEC filing, extract facts, save to Parquet.

    Args:
        ticker (str): The ticker symbol to process.
    """
    logger.info(f"Processing ticker: {ticker}")
    filing_path = download_sec_filings(ticker, OUTPUT_DIR)
    logger.info(f"Downloaded filing to: {filing_path}")
    facts = extract_top_facts(filing_path)
    logger.info(f"Extracted facts: {facts}")
    parquet_path = save_facts_to_parquet(ticker, facts, OUTPUT_DIR)
    logger.info(f"Saved facts to: {parquet_path}")

if __name__ == "__main__":
    watch_input_folder(INPUT_DIR, process_ticker)
