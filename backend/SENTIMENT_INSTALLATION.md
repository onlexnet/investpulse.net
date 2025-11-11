# Sentiment Analysis Module - Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Twitter Developer Account with API v2 access

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `tweepy>=4.14.0` - Twitter API client
- `transformers>=4.30.0` - Hugging Face transformers for sentiment analysis
- `torch>=2.0.0` - PyTorch for model execution
- `sentencepiece>=0.1.99` - Tokenizer support

## Step 2: Twitter API Setup

### Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use existing app
3. Navigate to "Keys and tokens"
4. Generate a "Bearer Token" (API v2)
5. Copy the Bearer Token

### Enable Filtered Stream Access

1. In the Twitter Developer Portal, ensure your app has access to:
   - Twitter API v2
   - Filtered stream endpoint
2. Review rate limits for your access level:
   - Essential: 50 rules, 50 requests/15min
   - Elevated: 50 rules, 50 requests/15min
   - Academic: 1000 rules, 300 requests/15min

## Step 3: Configure Environment

Copy the example environment file:

```bash
cp .env.sentiment.example .env.sentiment
```

Edit `.env.sentiment` and add your Twitter Bearer Token:

```bash
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

Optional: Customize other settings:

```bash
SENTIMENT_WINDOW_DAYS=5
MIN_CONFIDENCE_THRESHOLD=0.6
USE_GPU=false
MONITORED_ACCOUNTS=Benzinga,fxhedgers,ZeroHedge,Finviz_com,FT
TARGET_TICKERS=NVDA,MSFT,AAPL
```

## Step 4: Download Sentiment Model

On first run, the sentiment model will be automatically downloaded (~500MB).

To pre-download the model:

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print("Model downloaded successfully!")
```

## Step 5: Test Installation

Run the test suite:

```bash
pytest tests/test_sentiment.py -v
```

Expected output:
```
tests/test_sentiment.py::TestSentimentConfig::test_default_configuration PASSED
tests/test_sentiment.py::TestSentimentConfig::test_add_ticker PASSED
...
======================== XX passed in X.XXs ========================
```

## Step 6: Run Example

Test with the example script:

```bash
python src/sentiment_example.py
```

Expected output:
```
INFO - Initializing sentiment analysis system...
INFO - Starting Twitter stream monitoring...
INFO - Monitoring accounts: Benzinga, fxhedgers, ZeroHedge, Finviz_com, FT
INFO - Target tickers: NVDA, MSFT, AAPL
INFO - Connecting to filtered stream...
```

Press `Ctrl+C` to stop and see final sentiment report.

## GPU Support (Optional)

For faster sentiment analysis using GPU:

### NVIDIA GPU with CUDA

1. Install CUDA Toolkit (11.7 or higher)
2. Install PyTorch with CUDA support:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. Enable GPU in configuration:

```python
config = SentimentConfig(
    use_gpu=True
)
```

Or in `.env.sentiment`:
```bash
USE_GPU=true
```

Verify GPU is available:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

## Troubleshooting

### Issue: "Import tweepy could not be resolved"

**Solution:** Ensure tweepy is installed:
```bash
pip install tweepy>=4.14.0
```

### Issue: "Twitter bearer token not configured"

**Solution:** Set the bearer token in your configuration:
```python
config.twitter_bearer_token = "your_token_here"
```

Or use environment variable:
```bash
export TWITTER_BEARER_TOKEN="your_token_here"
```

### Issue: "Connection timeout" or "429 Rate Limit"

**Solution:** Twitter API has rate limits. Wait and retry, or:
- Check your API access level
- Reduce the number of monitored accounts
- Increase `stream_timeout` in config

### Issue: Model download fails

**Solution:** 
```bash
# Manual download with cache
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment'); AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment')"
```

### Issue: "CUDA out of memory"

**Solution:**
- Set `use_gpu=False` to use CPU
- Reduce batch size
- Use a smaller model

### Issue: No tweets captured

**Possible causes:**
1. No tweets from monitored accounts mentioning target tickers
2. Stream rules not properly configured
3. Bearer token invalid or expired

**Check:**
```python
# Verify stream rules
from src.sentiment import TwitterStreamMonitor, SentimentConfig
config = SentimentConfig(twitter_bearer_token="your_token")
monitor = TwitterStreamMonitor(config)
monitor.client = monitor._create_client()
rules = monitor.client.get_rules()
print(rules)
```

## Integration with Main App

To integrate sentiment analysis with the main trading app:

```python
# In src/app.py
from src.sentiment import (
    SentimentConfig,
    SentimentAnalyzer,
    SentimentAggregator
)

# Initialize sentiment components
sentiment_config = SentimentConfig(
    twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
)
sentiment_analyzer = SentimentAnalyzer(sentiment_config)
sentiment_aggregator = SentimentAggregator(sentiment_config)

# Use in processing workflow
def process_ticker_with_sentiment(ticker: str):
    # Get weighted sentiment
    weighted_sentiment = sentiment_aggregator.get_weighted_sentiment(ticker)
    
    # Include in decision making
    if weighted_sentiment:
        print(f"Sentiment for {ticker}: {weighted_sentiment.sentiment_direction}")
        print(f"Score: {weighted_sentiment.weighted_score:.4f}")
```

## Performance Optimization

### CPU-only Environment
- Expected throughput: 5-10 tweets/second
- Model inference: ~100-200ms per tweet

### GPU Environment (CUDA)
- Expected throughput: 20-50 tweets/second
- Model inference: ~10-20ms per tweet

### Memory Usage
- Base Python process: ~100MB
- Model loaded (CPU): ~500MB
- Model loaded (GPU): ~500MB GPU memory + ~200MB RAM
- Per tweet history: ~1-2KB

### Recommendations
- Run sentiment analysis in separate process/thread
- Use GPU for high-volume scenarios
- Clear old sentiments periodically (every hour)
- Implement result caching for repeated queries

## Next Steps

1. Read [src/sentiment/README.md](src/sentiment/README.md) for detailed API documentation
2. Explore `src/sentiment_example.py` for usage examples
3. Run tests: `pytest tests/test_sentiment.py`
4. Integrate with your trading strategy
5. Monitor and tune confidence thresholds

## Support

For issues or questions:
- Check existing GitHub issues
- Review Twitter API v2 documentation
- Check transformers library documentation
