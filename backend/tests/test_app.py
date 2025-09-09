from src.app import process_ticker
import os
import pandas as pd

def test_process_ticker_creates_parquet() -> None:
    """
    Test that process_ticker creates a Parquet file with 10 facts for the ticker.
    """
    ticker = 'AAPL'
    process_ticker(ticker)
    file_path = os.path.join('output', f'{ticker}_facts.parquet')
    assert os.path.exists(file_path)
    df = pd.read_parquet(file_path)
    assert len(df) == 10
    os.remove(file_path)
