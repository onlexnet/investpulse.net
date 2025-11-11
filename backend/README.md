## Predictive Trading Python App

This app watches the `input/entry/` folder for JSON files containing a ticker symbol, downloads SEC EDGAR filings for that ticker, extracts the top 10 most useful facts for buy/sell decisions, and saves them in Parquet format in the `output/` folder.

### New: Sentiment Analysis Module 📊

The app now includes a comprehensive sentiment analysis module that monitors Twitter for financial news and calculates weighted sentiment scores for stock tickers.

**Quick Links:**
- 🚀 [Quick Start Guide](SENTIMENT_QUICKSTART.md) - Get started in 5 minutes
- 📚 [Full Documentation](docs/SENTIMENT_DOCUMENTATION.md) - Complete API reference
- 🔧 [Installation Guide](SENTIMENT_INSTALLATION.md) - Detailed setup instructions
- 📖 [Module README](src/sentiment/README.md) - Module overview
- 💡 [Example Code](src/sentiment_example.py) - Usage examples

**Features:**
- Monitor Twitter Filtered Stream API for financial news accounts
- Analyze sentiment using transformer models (positive/negative/neutral)
- Calculate weighted sentiment scores based on engagement and time decay
- Track multiple tickers (NVDA, MSFT, AAPL, etc.)
- GPU support for faster analysis

**Note:** Sentiment module requires additional dependencies. To install:
```bash
pip install tweepy transformers torch sentencepiece
```

### Quick Start
1. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
2. Type checking with mypy:
	```bash
	mypy src/
	```
3. Run the app:
	```bash
	python -m src.app
	```

### Run Tests
To run all tests:
```bash
pytest tests
```

### Type Checking
This project uses mypy for strict type checking. Run type checking on the source code:
```bash
mypy src/
```

For type checking the entire project including tests:
```bash
mypy .
```
3. Add a JSON file to the `input/entry/` folder, e.g.:
	```json
	{ "ticker": "AAPL" }
	```
4. The app will:
	- Download dummy SEC filing for `AAPL`
	- Extract 10 facts
	- Save them to `output/AAPL_facts.parquet`

### Example Output
The Parquet file will contain facts like:
| fact                 | value   |
|----------------------|---------|
| Revenue Growth       | 10%     |
| Net Income           | $1M     |
| ...                  | ...     |

---
For details, see `DEVELOPMENT_PLAN.md`.
