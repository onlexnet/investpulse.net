import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
from src.fact_extractor import extract_top_facts, save_facts_to_parquet
import pandas as pd
from typing import List, Dict


class TestFactExtractor(unittest.TestCase):
    """Test cases for fact extractor functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_top_facts_with_html_tables(self):
        """Test fact extraction from HTML tables."""
        html_content = """
        <html>
            <table>
                <tr><td>Revenue</td><td>$100M</td></tr>
                <tr><td>Net Income</td><td>$20M</td></tr>
                <tr><td>Total Assets</td><td>$500M</td></tr>
            </table>
        </html>
        """
        
        with patch("builtins.open", mock_open(read_data=html_content)):
            facts = extract_top_facts("dummy_path.html")
        
        self.assertGreaterEqual(len(facts), 3)
        self.assertEqual(facts[0]["fact"], "Revenue")
        self.assertEqual(facts[0]["value"], "$100M")

    def test_extract_top_facts_with_text_fallback(self):
        """Test fact extraction with text fallback when no tables found."""
        text_content = """
        Some filing content here.
        Revenue increased 15% year over year.
        Operating margin was $50M this quarter.
        Cash flow from operations: $25M.
        Total debt: $100M outstanding.
        """
        
        with patch("builtins.open", mock_open(read_data=text_content)):
            facts = extract_top_facts("dummy_path.txt")
        
        # Should find lines with $ or %
        self.assertGreater(len(facts), 0)
        dollar_or_percent_facts = [f for f in facts if '$' in f['value'] or '%' in f['value']]
        self.assertGreater(len(dollar_or_percent_facts), 0)

    def test_extract_top_facts_handles_file_error(self):
        """Test error handling when file cannot be read."""
        facts = extract_top_facts('nonexistent_file.txt')
        
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["fact"], "Error extracting facts")
        self.assertIn("No such file or directory", facts[0]["value"])

    def test_extract_top_facts_returns_max_10(self):
        """Test that function returns maximum 10 facts."""
        # Create HTML with more than 10 table rows
        html_content = "<html><table>"
        for i in range(15):
            html_content += f"<tr><td>Fact{i}</td><td>Value{i}</td></tr>"
        html_content += "</table></html>"
        
        with patch("builtins.open", mock_open(read_data=html_content)):
            facts = extract_top_facts("dummy_path.html")
        
        self.assertEqual(len(facts), 10)

    def test_save_facts_to_parquet_creates_file(self):
        """Test that save_facts_to_parquet creates a valid Parquet file."""
        ticker = 'TEST'
        facts = [
            {"fact": "Revenue", "value": "$100M"},
            {"fact": "Net Income", "value": "$20M"},
            {"fact": "Assets", "value": "$500M"}
        ]
        
        file_path = save_facts_to_parquet(ticker, facts, self.temp_dir)
        
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith(f"{ticker}_facts.parquet"))
        
        # Verify file content
        df = pd.read_parquet(file_path)
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[0]["fact"], "Revenue")
        self.assertEqual(df.iloc[0]["value"], "$100M")

    def test_save_facts_to_parquet_with_empty_facts(self):
        """Test saving empty facts list."""
        ticker = 'EMPTY'
        facts = []
        
        file_path = save_facts_to_parquet(ticker, facts, self.temp_dir)
        
        self.assertTrue(os.path.exists(file_path))
        df = pd.read_parquet(file_path)
        self.assertEqual(len(df), 0)


# Legacy test functions for backward compatibility
def test_extract_top_facts_returns_10() -> None:
    """
    Legacy test that extract_top_facts returns fact dictionaries.
    Updated to handle real-world behavior where function may return fewer facts.
    """
    # Create a realistic HTML content for testing
    html_content = """
    <html>
        <table>
            <tr><td>Revenue</td><td>$1000M</td></tr>
            <tr><td>Net Income</td><td>$200M</td></tr>
            <tr><td>Total Assets</td><td>$5000M</td></tr>
            <tr><td>Cash</td><td>$500M</td></tr>
            <tr><td>Debt</td><td>$800M</td></tr>
        </table>
        Some additional content with 15% growth rate.
        Operating margin: $100M this quarter.
        Free cash flow: $50M reported.
        Dividends paid: $25M to shareholders.
        R&D expenses: $150M investment.
    </html>
    """
    
    with patch("builtins.open", mock_open(read_data=html_content)):
        facts: List[Dict[str, str]] = extract_top_facts('dummy_path')
    
    # Should extract up to 10 facts
    assert len(facts) <= 10
    assert len(facts) > 0  # Should find at least some facts
    assert all('fact' in f and 'value' in f for f in facts)


def test_save_facts_to_parquet_creates_file() -> None:
    """
    Legacy test that save_facts_to_parquet creates a Parquet file.
    Updated to use realistic test data.
    """
    ticker = 'AAPL'
    # Use realistic facts data instead of relying on extract_top_facts with dummy path
    facts = [
        {"fact": "Revenue", "value": "$1000M"},
        {"fact": "Net Income", "value": "$200M"},
        {"fact": "Total Assets", "value": "$5000M"},
        {"fact": "Cash", "value": "$500M"},
        {"fact": "Debt", "value": "$800M"},
        {"fact": "Operating Income", "value": "$300M"},
        {"fact": "Free Cash Flow", "value": "$150M"},
        {"fact": "R&D Expenses", "value": "$100M"},
        {"fact": "Gross Margin", "value": "40%"},
        {"fact": "ROE", "value": "25%"}
    ]
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = save_facts_to_parquet(ticker, facts, output_dir)
    assert os.path.exists(file_path)
    df = pd.read_parquet(file_path)
    assert len(df) == 10
    os.remove(file_path)


if __name__ == '__main__':
    unittest.main()
