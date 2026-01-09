# Sentiment Analysis Module

## Overview

The `src/sentiment` module provides a complete sentiment analysis system for financial news from Twitter. The system monitors selected financial accounts on Twitter, analyzes sentiment of posts related to specific stock tickers, and calculates weighted sentiment scores.

## Features

### 1. Twitter Stream API Monitoring
- Monitors Twitter Filtered Stream API v2
- Tracks accounts: @Benzinga, @fxhedgers, @ZeroHedge, @Finviz_com, @FT
- Automatically filters posts containing tickers (e.g., NVDA, MSFT, AAPL)
- Collects engagement metrics (retweets, likes)

### 2. Sentiment Analysis
- Uses transformer model `cardiffnlp/twitter-roberta-base-sentiment`
- Classifies posts as: positive, negative, neutral
- Calculates confidence score (0.0 - 1.0)
- Filters results by minimum confidence threshold

### 3. Weighted Sentiment Aggregation
- Calculates weighted sentiment for each ticker
- Considers the last 5 days (configurable)
- Weights based on:
  - Number of retweets (2x weight)
  - Number of likes (1x weight)
  - Analysis confidence score
  - Time decay (exponential, half-life 2 days)

## Module Structure

```
src/sentiment/
├── __init__.py              # Module exports
├── config.py                # Configuration
├── models.py                # Data models
├── twitter_stream.py        # Twitter Stream Monitor
├── sentiment_analyzer.py    # Sentiment analysis
└── sentiment_aggregator.py  # Aggregation and weighting
```

## Usage

### Basic Configuration

```python
from src.sentiment import SentimentConfig

config = SentimentConfig(
    twitter_bearer_token="YOUR_TOKEN_HERE",
    monitored_accounts=['Benzinga', 'fxhedgers', 'ZeroHedge', 'Finviz_com', 'FT'],
    target_tickers={'NVDA', 'MSFT', 'AAPL'},
    sentiment_window_days=5,
    min_confidence_threshold=0.6,
    use_gpu=False
)
```

### Stream Monitoring

```python
from src.sentiment import (
    TwitterStreamMonitor,
    SentimentAnalyzer,
    SentimentAggregator
)

# Initialize components
analyzer = SentimentAnalyzer(config)
aggregator = SentimentAggregator(config)

# Callback for new tweets
def on_tweet(tweet_data):
    result = analyzer.analyze(tweet_data)
    if result and result.is_reliable:
        aggregator.add_sentiment_result(result)

# Start monitoring
monitor = TwitterStreamMonitor(config, on_tweet_callback=on_tweet)
monitor.start()
```

### Getting Weighted Sentiment

```python
# For a single ticker
weighted_sentiment = aggregator.get_weighted_sentiment('NVDA')
print(f"Ticker: {weighted_sentiment.ticker}")
print(f"Direction: {weighted_sentiment.sentiment_direction}")  # BULLISH/BEARISH/NEUTRAL
print(f"Score: {weighted_sentiment.weighted_score:.4f}")  # -1.0 to 1.0
print(f"Total Tweets: {weighted_sentiment.total_tweets}")

# For all tickers
all_sentiments = aggregator.get_all_weighted_sentiments()
for ticker, sentiment in all_sentiments.items():
    print(f"{ticker}: {sentiment.sentiment_direction} ({sentiment.weighted_score:.4f})")
```

## Data Models

### TweetData
Represents a single tweet with engagement metrics:
- `tweet_id`: Tweet ID
- `text`: Tweet content
- `author_username`: Username
- `created_at`: Creation time
- `retweet_count`: Number of retweets
- `like_count`: Number of likes
- `mentioned_tickers`: List of tickers in the tweet

### SentimentResult
Sentiment analysis result:
- `sentiment`: Label (POSITIVE/NEGATIVE/NEUTRAL)
- `confidence`: Confidence level (0.0-1.0)
- `scores`: Detailed scores for each class

### WeightedSentiment
Aggregated sentiment for a ticker:
- `ticker`: Ticker symbol
- `weighted_score`: Weighted score (-1.0 to 1.0)
- `sentiment_direction`: BULLISH/BEARISH/NEUTRAL
- `positive_weight`: Sum of positive weights
- `negative_weight`: Sum of negative weights
- `neutral_weight`: Sum of neutral weights
- `total_tweets`: Number of analyzed tweets
- `average_confidence`: Average confidence

## Requirements

### Twitter API
- Twitter API v2 Bearer Token
- Access to Filtered Stream API

### Python Libraries
```
tweepy>=4.14.0
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
```

## Configuration

### Environment Variables
```bash
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

### Configuration Parameters

| Parameter | Type | Default Value | Description |
|----------|-----|---------------|-------------|
| `monitored_accounts` | List[str] | ['Benzinga', 'fxhedgers', 'ZeroHedge', 'Finviz_com', 'FT'] | Accounts to monitor |
| `target_tickers` | Set[str] | {'NVDA', 'MSFT', 'AAPL'} | Tickers to analyze |
| `sentiment_window_days` | int | 5 | Time window for aggregation |
| `min_confidence_threshold` | float | 0.6 | Minimum confidence threshold |
| `sentiment_model` | str | "cardiffnlp/twitter-roberta-base-sentiment" | Transformer model |
| `use_gpu` | bool | False | Use GPU for analysis |

## Weighting Algorithm

Each tweet's weight is calculated as:

```
weight = engagement_weight × confidence_weight × time_decay_weight

where:
- engagement_weight = 1.0 + (retweet_count × 2 + like_count) / 100
- confidence_weight = confidence_score (0.0-1.0)
- time_decay_weight = 0.5^(age_days / 2.0)
```

Weighted score for a ticker:
```
weighted_score = (positive_weight - negative_weight) / total_weight
```

Result ranges from -1.0 (very bearish) to 1.0 (very bullish).

## Complete Example

See `src/sentiment_example.py` for a complete usage example.

```bash
python src/sentiment_example.py
```

## Notes

1. **Rate Limits**: Twitter API has limits. The system automatically handles rate limiting.
2. **Memory**: The aggregator stores sentiment history. Use `clear_old_sentiments()` to clear old data.
3. **Model**: First run will download the model (~500MB). Subsequent runs will be faster.
4. **GPU**: For faster analysis, set `use_gpu=True` if you have a CUDA GPU available.

## Extensions

### Adding New Tickers
```python
config.add_ticker('TSLA')
config.add_ticker('GOOGL')
```

### Adding New Accounts
```python
config.add_account('WSJ')
config.add_account('BloombergMarkets')
```

### Data Export
```python
weighted_sentiment = aggregator.get_weighted_sentiment('NVDA')
data_dict = weighted_sentiment.to_dict()

# Save to JSON
import json
with open('sentiment_data.json', 'w') as f:
    json.dump(data_dict, f, indent=2)
```

## Testing

```bash
# Run unit tests
pytest tests/test_sentiment.py -v

# Test with mock data
python -m src.sentiment.twitter_stream --test
```

## Architecture Integration

The sentiment module can be integrated with the existing architecture through:

1. **Ray Workflow**: Sentiment analysis as a Ray task
2. **File Watcher**: Trigger analysis based on new files
3. **State Manager**: Track sentiment analysis state

Example Ray integration:
```python
import ray
from src.sentiment import SentimentAnalyzer

@ray.remote
class SentimentAnalysisActor:
    def __init__(self, config):
        self.analyzer = SentimentAnalyzer(config)
    
    def analyze_tweet(self, tweet_data):
        return self.analyzer.analyze(tweet_data)
```
