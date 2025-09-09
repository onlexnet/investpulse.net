
import pandas as pd
import os
from typing import List, Dict
from bs4 import BeautifulSoup

def extract_top_facts(filing_path: str) -> List[Dict[str, str]]:
    """
    Extract the top 10 most useful facts from a real SEC filing HTML or TXT file.
    Args:
        filing_path (str): Path to the SEC filing file.
    Returns:
        List[Dict[str, str]]: List of fact dictionaries.
    """
    facts: List[Dict[str, str]] = []
    try:
        with open(filing_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Try to parse as HTML
        soup = BeautifulSoup(content, "html.parser")
        # Example: Extract all table rows with financial data
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    fact_name = cells[0].get_text(strip=True)
                    fact_value = cells[1].get_text(strip=True)
                    if fact_name and fact_value:
                        facts.append({"fact": fact_name, "value": fact_value})
                if len(facts) >= 10:
                    break
            if len(facts) >= 10:
                break
        # Fallback: If not enough facts found, fill with lines containing '$' or '%'
        if len(facts) < 10:
            lines = content.splitlines()
            for line in lines:
                if ("$" in line or "%" in line) and len(line) < 100:
                    facts.append({"fact": "Extracted", "value": line.strip()})
                if len(facts) >= 10:
                    break
    except Exception as e:
        facts = [{"fact": "Error extracting facts", "value": str(e)}]
    return facts[:10]

def save_facts_to_parquet(ticker: str, facts: List[Dict[str, str]], output_dir: str) -> str:
    """
    Save extracted facts to a Parquet file.

    Args:
        ticker (str): The ticker symbol.
        facts (List[Dict[str, str]]): List of fact dictionaries.
        output_dir (str): Directory to save the Parquet file.

    Returns:
        str: Path to the saved Parquet file.
    """
    df = pd.DataFrame(facts)
    file_path = os.path.join(output_dir, f"{ticker}_facts.parquet")
    df.to_parquet(file_path)
    return file_path
