# DEVELOPMENT PLAN

## Overview
This document outlines the steps required to implement a Python application that:
- Watches a local subfolder for JSON files containing ticker information
- Downloads SEC EDGAR data (annual/quarterly) for each ticker
- Extracts the top 10 most useful facts for buy/sell decisions
- Stores extracted data in Parquet format in a local subfolder

---

## 1. Project Initialization
- Set up a Python virtual environment
- Install required libraries: `watchdog`, `requests`, `pandas`, `pyarrow`, `sec-edgar-downloader` (or custom SEC API code)
- Create main folders:
  - `input/` — for incoming JSON files
  - `output/` — for Parquet files
  - `src/` — for source code

## 2. File Watcher Implementation
- Use `watchdog` to monitor the `input/` folder for new JSON files
- On file creation, parse JSON to extract ticker symbol
- Validate JSON structure and ticker presence

## 3. SEC EDGAR Data Download
- For each ticker, use SEC EDGAR API or scraping to download annual (10-K) and quarterly (10-Q) filings
- Store raw filings temporarily if needed
- Handle rate limits and errors

## 4. Fact Extraction Logic
- Parse filings to extract financial and business facts
- Define criteria for "top 10" facts (e.g., revenue, net income, debt, cash flow, risk factors, management discussion)
- Rank and select the most useful facts for buy/sell decisions
- Structure extracted facts in a tabular format

## 5. Data Storage
- Use `pandas` to convert extracted facts to DataFrame
- Save DataFrame as Parquet file in `output/` folder
- Name files by ticker and date for easy retrieval

## 6. Error Handling & Logging
- Implement logging for file events, download status, extraction results, and errors
- Ensure robust error handling for all steps

## 7. Documentation & Testing
- Document setup, usage, and requirements in `README.md`
- Write unit tests for key functions (file watcher, downloader, extractor)
- Test end-to-end workflow with sample data

---

## Optional Enhancements
- Add CLI or GUI for manual operation
- Support batch processing of multiple tickers
- Integrate with cloud storage or databases
- Add configuration file for customizable parameters

---

## Next Steps
1. Set up project structure and environment
2. Implement file watcher
3. Develop SEC EDGAR downloader
4. Build fact extraction logic
5. Implement Parquet data storage
6. Add logging and error handling
7. Write documentation and tests
