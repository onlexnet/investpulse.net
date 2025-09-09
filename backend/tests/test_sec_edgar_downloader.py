import os
from src.sec_edgar_downloader import download_sec_filings

def test_download_sec_filings_creates_file() -> None:
    """
    Test that download_sec_filings creates a dummy file for the ticker.
    """
    ticker = 'AAPL'
    output_dir = 'output'
    file_path = download_sec_filings(ticker, output_dir)
    assert os.path.exists(file_path)
    with open(file_path) as f:
        content = f.read()
    assert 'Dummy SEC filing' in content
    os.remove(file_path)
