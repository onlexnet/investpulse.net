import os
from src.fact_extractor import extract_top_facts, save_facts_to_parquet
import pandas as pd
from typing import List, Dict

def test_extract_top_facts_returns_10() -> None:
    """
    Test that extract_top_facts returns 10 fact dictionaries.
    """
    facts: List[Dict[str, str]] = extract_top_facts('dummy_path')
    assert len(facts) == 10
    assert all('fact' in f and 'value' in f for f in facts)

def test_save_facts_to_parquet_creates_file() -> None:
    """
    Test that save_facts_to_parquet creates a Parquet file with 10 facts.
    """
    ticker = 'AAPL'
    facts = extract_top_facts('dummy_path')
    output_dir = 'output'
    file_path = save_facts_to_parquet(ticker, facts, output_dir)
    assert os.path.exists(file_path)
    df = pd.read_parquet(file_path)
    assert len(df) == 10
    os.remove(file_path)
