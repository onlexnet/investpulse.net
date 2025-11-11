# Sentiment Analysis Module - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Testing](#testing)
8. [Performance](#performance)

## Overview

Moduł `src/sentiment` to kompletny system analizy sentymentu dla wiadomości finansowych z Twittera, stworzony dla projektu InvestPulse.

### Główne Funkcjonalności

✅ **Twitter Stream Monitoring**
- Obserwacja Twitter Filtered Stream API v2
- Monitorowanie wybranych kont finansowych (@Benzinga, @fxhedgers, @ZeroHedge, @Finviz_com, @FT)
- Automatyczna ekstrakcja tickerów (NVDA, MSFT, AAPL)
- Zbieranie metryk zaangażowania (retweets, likes)

✅ **Sentiment Analysis**
- Model: `cardiffnlp/twitter-roberta-base-sentiment`
- Klasyfikacja: positive, negative, neutral
- Confidence scoring (0.0 - 1.0)
- GPU support dla szybszej analizy

✅ **Weighted Sentiment Aggregation**
- Okno czasowe: 5 dni (konfigurowalne)
- Wagi: retweets (2x), likes (1x), confidence, time decay
- Wynik: -1.0 (bearish) do 1.0 (bullish)
- Kierunek: BULLISH, BEARISH, NEUTRAL

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Twitter Stream                          │
│                  (Filtered Stream API v2)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              TwitterStreamMonitor                           │
│  - Connects to stream                                       │
│  - Filters by accounts                                      │
│  - Extracts tickers                                         │
│  - Collects metrics                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │    TweetData     │
            └────────┬─────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              SentimentAnalyzer                              │
│  - Preprocesses text                                        │
│  - Runs transformer model                                   │
│  - Calculates confidence                                    │
│  - Returns sentiment                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ SentimentResult  │
            └────────┬─────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           SentimentAggregator                               │
│  - Stores sentiment history                                 │
│  - Calculates time decay                                    │
│  - Computes engagement weights                              │
│  - Aggregates by ticker                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ WeightedSentiment│
            └──────────────────┘
```

## Installation

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Twitter API
cp .env.sentiment.example .env.sentiment
# Edit .env.sentiment and add your TWITTER_BEARER_TOKEN

# Run tests
pytest tests/test_sentiment.py -v

# Run example
python src/sentiment_example.py
```

Szczegółowa instrukcja: [SENTIMENT_INSTALLATION.md](SENTIMENT_INSTALLATION.md)

## Usage

### Basic Example

```python
from src.sentiment import (
    SentimentConfig,
    TwitterStreamMonitor,
    SentimentAnalyzer,
    SentimentAggregator
)

# Configure
config = SentimentConfig(
    twitter_bearer_token="YOUR_TOKEN",
    target_tickers={'NVDA', 'MSFT', 'AAPL'}
)

# Initialize components
analyzer = SentimentAnalyzer(config)
aggregator = SentimentAggregator(config)

# Process tweets
def on_tweet(tweet_data):
    result = analyzer.analyze(tweet_data)
    if result and result.is_reliable:
        aggregator.add_sentiment_result(result)

# Start monitoring
monitor = TwitterStreamMonitor(config, on_tweet_callback=on_tweet)
monitor.start()

# Get results
sentiments = aggregator.get_all_weighted_sentiments()
for ticker, sentiment in sentiments.items():
    print(f"{ticker}: {sentiment.sentiment_direction} ({sentiment.weighted_score:.4f})")
```

### Advanced Usage

#### Custom Configuration

```python
config = SentimentConfig(
    twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    monitored_accounts=['Benzinga', 'WSJ', 'BloombergMarkets'],
    target_tickers={'TSLA', 'GOOGL', 'AMZN'},
    sentiment_window_days=7,
    min_confidence_threshold=0.7,
    use_gpu=True,
    sentiment_model='cardiffnlp/twitter-roberta-base-sentiment'
)
```

#### Dynamic Ticker Management

```python
# Add/remove tickers dynamically
config.add_ticker('TSLA')
config.remove_ticker('AAPL')

# Add/remove accounts
config.add_account('WSJ')
config.remove_account('Finviz_com')
```

#### Export Results

```python
from src.sentiment.utils import (
    export_sentiments_to_json,
    format_sentiment_report
)

# Export to JSON
sentiments = aggregator.get_all_weighted_sentiments()
export_sentiments_to_json(sentiments, 'sentiment_output.json')

# Print formatted report
report = format_sentiment_report(sentiments)
print(report)
```

#### Filter Significant Sentiments

```python
from src.sentiment.utils import filter_significant_sentiments

# Only include sentiments with enough data
significant = filter_significant_sentiments(
    sentiments,
    min_tweets=10,
    min_confidence=0.7
)
```

## API Reference

### SentimentConfig

Configuration for sentiment analysis module.

**Attributes:**
- `monitored_accounts: List[str]` - Twitter accounts to monitor
- `target_tickers: Set[str]` - Stock tickers to analyze
- `sentiment_window_days: int` - Days to include in aggregation (default: 5)
- `twitter_bearer_token: str` - Twitter API v2 Bearer Token
- `min_confidence_threshold: float` - Min confidence to accept (default: 0.6)
- `use_gpu: bool` - Use GPU for analysis (default: False)
- `sentiment_model: str` - Transformer model name

**Methods:**
- `add_ticker(ticker: str)` - Add ticker to monitoring
- `remove_ticker(ticker: str)` - Remove ticker
- `add_account(account: str)` - Add Twitter account
- `remove_account(account: str)` - Remove Twitter account

### TwitterStreamMonitor

Monitor Twitter filtered stream for financial news.

**Constructor:**
```python
TwitterStreamMonitor(
    config: SentimentConfig,
    on_tweet_callback: Optional[Callable[[TweetData], None]] = None
)
```

**Methods:**
- `start()` - Start monitoring (blocking)
- `stop()` - Stop monitoring

### SentimentAnalyzer

Analyze sentiment using transformer models.

**Constructor:**
```python
SentimentAnalyzer(config: SentimentConfig)
```

**Methods:**
- `analyze(tweet_data: TweetData) -> Optional[SentimentResult]`
- `analyze_batch(tweets: List[TweetData]) -> List[SentimentResult]`
- `is_high_confidence(result: SentimentResult) -> bool`

### SentimentAggregator

Aggregate and calculate weighted sentiment scores.

**Constructor:**
```python
SentimentAggregator(config: SentimentConfig)
```

**Methods:**
- `add_sentiment_result(result: SentimentResult)` - Add result to history
- `get_weighted_sentiment(ticker: str, window_end: Optional[datetime]) -> Optional[WeightedSentiment]`
- `get_all_weighted_sentiments(window_end: Optional[datetime]) -> Dict[str, WeightedSentiment]`
- `clear_old_sentiments(cutoff_date: Optional[datetime]) -> int`

### Data Models

#### TweetData
```python
@dataclass
class TweetData:
    tweet_id: str
    text: str
    author_username: str
    created_at: datetime
    retweet_count: int = 0
    like_count: int = 0
    mentioned_tickers: List[str] = field(default_factory=list)
    
    @property
    def engagement_score(self) -> float
```

#### SentimentResult
```python
@dataclass
class SentimentResult:
    tweet_data: TweetData
    sentiment: SentimentLabel
    confidence: float
    scores: Dict[str, float]
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_reliable(self) -> bool
```

#### WeightedSentiment
```python
@dataclass
class WeightedSentiment:
    ticker: str
    weighted_score: float  # -1.0 to 1.0
    positive_weight: float
    negative_weight: float
    neutral_weight: float
    total_tweets: int
    window_start: datetime
    window_end: datetime
    average_confidence: float
    
    @property
    def sentiment_direction(self) -> str  # BULLISH/BEARISH/NEUTRAL
    
    def to_dict(self) -> Dict
```

## Examples

### Example 1: Real-time Monitoring

```python
import logging
from src.sentiment import *

logging.basicConfig(level=logging.INFO)

config = SentimentConfig(
    twitter_bearer_token="YOUR_TOKEN",
    target_tickers={'NVDA', 'MSFT'}
)

analyzer = SentimentAnalyzer(config)
aggregator = SentimentAggregator(config)

def on_tweet(tweet):
    result = analyzer.analyze(tweet)
    if result:
        aggregator.add_sentiment_result(result)
        print(f"📊 {tweet.mentioned_tickers[0]}: {result.sentiment.value}")

monitor = TwitterStreamMonitor(config, on_tweet)
monitor.start()
```

### Example 2: Batch Analysis

```python
from src.sentiment import *

# Load historical tweets
tweets = load_tweets_from_file('tweets.json')

analyzer = SentimentAnalyzer(config)
results = analyzer.analyze_batch(tweets)

for result in results:
    if result.is_reliable:
        print(f"{result.tweet_data.mentioned_tickers}: {result.sentiment.value}")
```

### Example 3: Sentiment Reporting

```python
from src.sentiment import *
from src.sentiment.utils import format_sentiment_report
import time

aggregator = SentimentAggregator(config)

# Collect data...

# Periodic reporting
while True:
    time.sleep(300)  # Every 5 minutes
    
    sentiments = aggregator.get_all_weighted_sentiments()
    report = format_sentiment_report(sentiments)
    print(report)
    
    # Cleanup
    aggregator.clear_old_sentiments()
```

## Testing

### Run All Tests

```bash
pytest tests/test_sentiment.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_sentiment.py::TestSentimentAggregator -v
```

### Test Coverage

```bash
pytest tests/test_sentiment.py --cov=src/sentiment --cov-report=html
```

### Manual Testing

```python
# Test configuration
from src.sentiment import SentimentConfig

config = SentimentConfig()
assert 'NVDA' in config.target_tickers
print("✓ Config test passed")

# Test models
from src.sentiment.models import TweetData
from datetime import datetime

tweet = TweetData(
    tweet_id="123",
    text="Test",
    author_username="test",
    created_at=datetime.now(),
    retweet_count=10,
    like_count=50
)
assert tweet.engagement_score == 70.0
print("✓ Models test passed")
```

## Performance

### Benchmarks

**CPU (Intel i7)**
- Tweet parsing: ~1ms
- Sentiment analysis: ~100-200ms per tweet
- Aggregation: ~5ms per ticker
- Throughput: ~5-10 tweets/second

**GPU (NVIDIA RTX 3080)**
- Tweet parsing: ~1ms
- Sentiment analysis: ~10-20ms per tweet
- Aggregation: ~5ms per ticker
- Throughput: ~20-50 tweets/second

### Memory Usage

- Base module: ~100MB
- Transformer model (loaded): ~500MB
- Per tweet in history: ~1-2KB
- Example: 10,000 tweets = ~10-20MB history

### Optimization Tips

1. **Use GPU** for high volume scenarios
2. **Batch analysis** when processing historical data
3. **Clear old sentiments** periodically
4. **Filter by confidence** early to reduce memory
5. **Use separate process** for stream monitoring

### Rate Limits

**Twitter API v2 (Filtered Stream)**
- Essential: 50 rules, 50 requests/15min
- Elevated: 50 rules, 50 requests/15min
- Academic: 1000 rules, 300 requests/15min

## Integration Examples

### Integration with Ray

```python
import ray
from src.sentiment import SentimentAnalyzer, SentimentConfig

@ray.remote
class SentimentAnalysisActor:
    def __init__(self):
        config = SentimentConfig()
        self.analyzer = SentimentAnalyzer(config)
    
    def analyze(self, tweet_data):
        return self.analyzer.analyze(tweet_data)

# Use
ray.init()
actor = SentimentAnalysisActor.remote()
result = ray.get(actor.analyze.remote(tweet_data))
```

### Integration with Processing Pipeline

```python
from src.sentiment import SentimentAggregator
from src.processing_state import ProcessingState

def process_ticker_with_sentiment(ticker: str, state: ProcessingState):
    # Get sentiment
    aggregator = SentimentAggregator(config)
    sentiment = aggregator.get_weighted_sentiment(ticker)
    
    # Add to state metadata
    if sentiment:
        state.add_metadata('sentiment_score', sentiment.weighted_score)
        state.add_metadata('sentiment_direction', sentiment.sentiment_direction)
        state.add_metadata('sentiment_confidence', sentiment.average_confidence)
    
    # Continue processing...
```

## Files Structure

```
src/sentiment/
├── __init__.py              # Module exports
├── config.py                # Configuration class
├── models.py                # Data models
├── twitter_stream.py        # Twitter API client
├── sentiment_analyzer.py    # Sentiment analysis
├── sentiment_aggregator.py  # Aggregation logic
├── utils.py                 # Utility functions
└── README.md               # Detailed docs

tests/
└── test_sentiment.py        # Unit tests

docs/
├── SENTIMENT_INSTALLATION.md  # Installation guide
└── SENTIMENT_DOCUMENTATION.md # This file

src/sentiment_example.py     # Usage example
.env.sentiment.example       # Config template
```

## Troubleshooting

See [SENTIMENT_INSTALLATION.md](SENTIMENT_INSTALLATION.md) for detailed troubleshooting.

## Contributing

When contributing to sentiment module:

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings (Google style)
4. Add unit tests for new features
5. Update documentation
6. Run mypy type checking

## License

Same as main project license.

## Support

- GitHub Issues: [Report bugs](https://github.com/onlexnet/investpulse.net/issues)
- Documentation: [Full docs](src/sentiment/README.md)
- Examples: [sentiment_example.py](src/sentiment_example.py)
