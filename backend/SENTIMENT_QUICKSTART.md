# Sentiment Analysis - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install tweepy transformers torch sentencepiece
```

### 2. Get Twitter API Token
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create app → Get Bearer Token
3. Copy the token

### 3. Create & Run

**Create `quick_sentiment.py`:**

```python
import os
from src.sentiment import (
    SentimentConfig,
    TwitterStreamMonitor,
    SentimentAnalyzer,
    SentimentAggregator
)

# Configure
config = SentimentConfig(
    twitter_bearer_token="YOUR_BEARER_TOKEN_HERE",
    target_tickers={'NVDA', 'MSFT', 'AAPL'}
)

# Initialize
analyzer = SentimentAnalyzer(config)
aggregator = SentimentAggregator(config)

# Process tweets
def on_tweet(tweet):
    result = analyzer.analyze(tweet)
    if result and result.is_reliable:
        aggregator.add_sentiment_result(result)
        print(f"✓ {tweet.mentioned_tickers[0]}: {result.sentiment.value}")

# Start
print("🎯 Monitoring Twitter for NVDA, MSFT, AAPL...")
monitor = TwitterStreamMonitor(config, on_tweet_callback=on_tweet)

try:
    monitor.start()
except KeyboardInterrupt:
    print("\n📊 Final Results:")
    sentiments = aggregator.get_all_weighted_sentiments()
    for ticker, s in sentiments.items():
        print(f"{ticker}: {s.sentiment_direction} ({s.weighted_score:+.4f})")
```

**Run:**
```bash
python quick_sentiment.py
```

### 4. See Results

After a few minutes, press Ctrl+C to see results:

```
📊 Final Results:
NVDA: BULLISH (+0.4523)
MSFT: NEUTRAL (+0.0812)
AAPL: BEARISH (-0.2341)
```

## 📚 Next Steps

- Read [full documentation](docs/SENTIMENT_DOCUMENTATION.md)
- See [advanced examples](src/sentiment_example.py)
- Check [installation guide](SENTIMENT_INSTALLATION.md)
- Run [tests](tests/test_sentiment.py)

## 🔧 Configuration Options

```python
config = SentimentConfig(
    twitter_bearer_token="token",        # Required
    target_tickers={'NVDA', 'MSFT'},     # Tickers to track
    monitored_accounts=['Benzinga'],     # Accounts to monitor
    sentiment_window_days=5,             # Aggregation window
    min_confidence_threshold=0.6,        # Min confidence
    use_gpu=False                        # Use GPU
)
```

## 💡 Tips

- **First run** downloads model (~500MB), takes ~2 minutes
- **Rate limits**: Twitter API limits requests per 15 minutes
- **GPU**: Set `use_gpu=True` for 5-10x faster analysis
- **Memory**: Clears old data automatically after 10 days

## 🐛 Common Issues

### "Import tweepy could not be resolved"
```bash
pip install tweepy>=4.14.0
```

### "Bearer token not configured"
Check your token is correct and has Filtered Stream access.

### "No tweets captured"
Wait a few minutes - tweets need to mention your target tickers.

## 📊 Understanding Results

**weighted_score**: -1.0 to +1.0
- `> 0.2` = BULLISH 📈
- `-0.2 to 0.2` = NEUTRAL ➡️
- `< -0.2` = BEARISH 📉

**Calculated from:**
- Sentiment of tweets (positive/negative/neutral)
- Engagement (retweets × 2 + likes)
- Confidence scores
- Time decay (recent tweets weighted higher)

## 🎯 Integration Example

Add to your trading strategy:

```python
from src.sentiment import SentimentAggregator

# Get sentiment
aggregator = SentimentAggregator(config)
nvda_sentiment = aggregator.get_weighted_sentiment('NVDA')

# Use in decision
if nvda_sentiment and nvda_sentiment.sentiment_direction == 'BULLISH':
    print("Strong positive sentiment on NVDA")
    # Your trading logic here
```

## 📖 Full Documentation

- **Detailed guide**: [docs/SENTIMENT_DOCUMENTATION.md](docs/SENTIMENT_DOCUMENTATION.md)
- **Installation**: [SENTIMENT_INSTALLATION.md](SENTIMENT_INSTALLATION.md)
- **Module API**: [src/sentiment/README.md](src/sentiment/README.md)
- **Examples**: [src/sentiment_example.py](src/sentiment_example.py)

## 🆘 Help

- GitHub Issues: https://github.com/onlexnet/investpulse.net/issues
- Twitter API Docs: https://developer.twitter.com/en/docs
- Transformers Docs: https://huggingface.co/docs/transformers
