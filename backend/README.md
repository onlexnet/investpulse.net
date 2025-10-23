## Predictive Trading Python App

This app watches the `input/` folder for JSON files containing a ticker symbol, downloads SEC EDGAR filings for that ticker, extracts the top 10 most useful facts for buy/sell decisions, and saves them in Parquet format in the `output/` folder.

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

Or use the convenience script:
```bash
./typecheck.sh
```

For type checking the entire project including tests:
```bash
mypy .
```
3. Add a JSON file to the `input/` folder, e.g.:
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
