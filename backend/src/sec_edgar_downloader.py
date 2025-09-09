import os
from sec_edgar_downloader import Downloader

def download_sec_filings(ticker: str, output_dir: str, form_type: str = "10-Q", count: int = 1, email_address: str = "contact@onlex.net") -> str:
    """
    Download the latest SEC filing for the given ticker using sec-edgar-downloader.
    Returns the path to the latest downloaded filing.
    Args:
        ticker (str): The ticker symbol.
        output_dir (str): Directory to save the filing (not used, kept for compatibility).
        form_type (str): SEC form type (default: "10-Q").
        count (int): Number of filings to download (default: 1).
        email_address (str): Email address required by SEC for downloader.
    Returns:
        str: Path to the latest downloaded filing file.
    """
    dl = Downloader(email_address, os.path.join(os.getcwd(), "sec-edgar-filings"))
    dl.get(form_type, ticker, limit=count)
    filings_dir = os.path.join("sec-edgar-filings", ticker, form_type)
    
    # Find the latest filing directory
    filing_dirs = sorted(os.listdir(filings_dir), reverse=True)
    if filing_dirs:
        latest_filing_dir = os.path.join(filings_dir, filing_dirs[0])
        # Look for the actual filing file within the directory
        filing_files = [f for f in os.listdir(latest_filing_dir) if f.endswith(('.htm', '.html', '.txt'))]
        if filing_files:
            return os.path.join(latest_filing_dir, filing_files[0])
        else:
            raise FileNotFoundError(f"No filing files found in directory: {latest_filing_dir}")
    else:
        raise FileNotFoundError(f"No filings found for ticker: {ticker}")
