# Sentiment Analysis - Example Output

## Example 1: Real-time Tweet Processing

```
🎯 Monitoring Twitter for NVDA, MSFT, AAPL...
INFO - Starting Twitter stream monitor
INFO - Added 5 stream rules for accounts: Benzinga, fxhedgers, ZeroHedge, Finviz_com, FT
INFO - Connecting to filtered stream...

✓ NVDA: positive (confidence: 0.87, engagement: 234)
  Tweet: "Nvidia crushing earnings expectations! $NVDA revenue up 265% YoY"
  
✓ MSFT: neutral (confidence: 0.71, engagement: 89)
  Tweet: "Microsoft Azure growth steady at 29% - in line with expectations $MSFT"
  
✓ NVDA: positive (confidence: 0.92, engagement: 567)
  Tweet: "$NVDA stock soars on AI chip demand - analysts raising price targets"
  
✓ AAPL: negative (confidence: 0.78, engagement: 156)
  Tweet: "Apple iPhone sales miss estimates in China market $AAPL"
  
✓ MSFT: positive (confidence: 0.84, engagement: 312)
  Tweet: "Microsoft wins major government cloud contract, $MSFT shares surge"
```

## Example 2: Weighted Sentiment Report

```
============================================================
SENTIMENT ANALYSIS REPORT
============================================================
Generated: 2025-11-10 14:30:00

NVDA
------------------------------
  Direction:        BULLISH
  Weighted Score:   +0.6234
  Total Tweets:     47
  Avg Confidence:   0.812
  Positive Weight:  78.45
  Negative Weight:  12.34
  Neutral Weight:   18.92
  Window:           2025-11-05 to 2025-11-10

MSFT
------------------------------
  Direction:        BULLISH
  Weighted Score:   +0.2847
  Total Tweets:     32
  Avg Confidence:   0.753
  Positive Weight:  45.23
  Negative Weight:  28.91
  Neutral Weight:   15.67
  Window:           2025-11-05 to 2025-11-10

AAPL
------------------------------
  Direction:        NEUTRAL
  Weighted Score:   +0.0912
  Total Tweets:     28
  Avg Confidence:   0.698
  Positive Weight:  32.45
  Negative Weight:  29.87
  Neutral Weight:   21.34
  Window:           2025-11-05 to 2025-11-10

============================================================
```

## Example 3: JSON Export

```json
{
  "timestamp": "2025-11-10T14:30:00.123456",
  "sentiments": {
    "NVDA": {
      "ticker": "NVDA",
      "weighted_score": 0.6234,
      "sentiment_direction": "BULLISH",
      "positive_weight": 78.45,
      "negative_weight": 12.34,
      "neutral_weight": 18.92,
      "total_tweets": 47,
      "average_confidence": 0.812,
      "window_start": "2025-11-05T14:30:00.000000",
      "window_end": "2025-11-10T14:30:00.000000"
    },
    "MSFT": {
      "ticker": "MSFT",
      "weighted_score": 0.2847,
      "sentiment_direction": "BULLISH",
      "positive_weight": 45.23,
      "negative_weight": 28.91,
      "neutral_weight": 15.67,
      "total_tweets": 32,
      "average_confidence": 0.753,
      "window_start": "2025-11-05T14:30:00.000000",
      "window_end": "2025-11-10T14:30:00.000000"
    },
    "AAPL": {
      "ticker": "AAPL",
      "weighted_score": 0.0912,
      "sentiment_direction": "NEUTRAL",
      "positive_weight": 32.45,
      "negative_weight": 29.87,
      "neutral_weight": 21.34,
      "total_tweets": 28,
      "average_confidence": 0.698,
      "window_start": "2025-11-05T14:30:00.000000",
      "window_end": "2025-11-10T14:30:00.000000"
    }
  }
}
```

## Example 4: Sentiment Over Time

```
Time Series Analysis for NVDA (last 5 days)
------------------------------------------------------------
Day 1 (2025-11-05): +0.4521  [BULLISH] (12 tweets)
Day 2 (2025-11-06): +0.5234  [BULLISH] (15 tweets)
Day 3 (2025-11-07): +0.6012  [BULLISH] (18 tweets)
Day 4 (2025-11-08): +0.6789  [BULLISH] (21 tweets)
Day 5 (2025-11-09): +0.7123  [BULLISH] (23 tweets)

Trend: ⬆️ Increasing bullish sentiment
Change: +0.2602 (+57.5%)
```

## Example 5: Filtered Significant Sentiments

```python
# Only show sentiments with >= 10 tweets and >= 0.7 confidence
from src.sentiment.utils import filter_significant_sentiments

significant = filter_significant_sentiments(
    sentiments,
    min_tweets=10,
    min_confidence=0.7
)

# Output:
{
  "NVDA": WeightedSentiment(
    ticker="NVDA",
    weighted_score=0.6234,
    total_tweets=47,
    average_confidence=0.812
  )
}
# MSFT and AAPL filtered out due to not meeting criteria
```

## Example 6: Sentiment Summary Statistics

```python
from src.sentiment.utils import get_sentiment_summary

summary = get_sentiment_summary(sentiments)

# Output:
{
  'bullish': 15,
  'bearish': 3,
  'neutral': 7
}

# Interpretation:
# 15 tickers showing bullish sentiment
# 3 tickers showing bearish sentiment
# 7 tickers showing neutral sentiment
```

## Example 7: Integration with Trading Strategy

```python
# Get sentiment for trading decision
def should_buy(ticker: str) -> bool:
    sentiment = aggregator.get_weighted_sentiment(ticker)
    
    if not sentiment:
        return False
    
    # Buy criteria:
    # 1. Strong bullish sentiment (> 0.5)
    # 2. High confidence (> 0.75)
    # 3. Significant data (> 15 tweets)
    return (
        sentiment.weighted_score > 0.5 and
        sentiment.average_confidence > 0.75 and
        sentiment.total_tweets > 15
    )

# Usage
for ticker in ['NVDA', 'MSFT', 'AAPL']:
    if should_buy(ticker):
        print(f"✅ BUY signal for {ticker}")
    else:
        print(f"⏸️  HOLD/SKIP {ticker}")

# Output:
# ✅ BUY signal for NVDA
# ⏸️  HOLD/SKIP MSFT
# ⏸️  HOLD/SKIP AAPL
```

## Example 8: Real Tweet Examples

### Positive Sentiment (NVDA)
```
Original Tweet:
"BREAKING: @nvidia announces new AI chip 40% faster than competitors! 
$NVDA stock surging in after-hours trading. Wall Street analysts 
scrambling to raise price targets. This is huge for AI infrastructure."

Analysis Result:
- Sentiment: POSITIVE
- Confidence: 0.94
- Engagement: retweets=542, likes=2,134
- Engagement Score: 3,218
- Weight in Aggregation: 4.82 (high due to recent + high engagement)
```

### Negative Sentiment (AAPL)
```
Original Tweet:
"Apple iPhone 15 sales disappointing in key China market. 
$AAPL losing ground to local competitors. Market share down 
15% YoY according to latest data."

Analysis Result:
- Sentiment: NEGATIVE
- Confidence: 0.86
- Engagement: retweets=234, likes=876
- Engagement Score: 1,344
- Weight in Aggregation: 2.01
```

### Neutral Sentiment (MSFT)
```
Original Tweet:
"Microsoft reports Q3 results: Azure cloud revenue +29%, 
Office 365 +14%, Gaming +12%. Results in line with expectations. 
$MSFT shares flat in after-hours."

Analysis Result:
- Sentiment: NEUTRAL
- Confidence: 0.72
- Engagement: retweets=67, likes=289
- Engagement Score: 423
- Weight in Aggregation: 0.63
```

## Example 9: Time Decay Effect

```
Same tweet analyzed at different times:

Tweet: "Nvidia crushes earnings! $NVDA"
Base engagement: 1000 (500 retweets, 500 likes)
Base weight: 1.5 (engagement factor)

Age 0 hours:  weight = 1.50 × 1.00 = 1.50  [100% impact]
Age 12 hours: weight = 1.50 × 0.95 = 1.43  [95% impact]
Age 24 hours: weight = 1.50 × 0.84 = 1.26  [84% impact]
Age 48 hours: weight = 1.50 × 0.71 = 1.07  [71% impact]
Age 96 hours: weight = 1.50 × 0.50 = 0.75  [50% impact]

Note: Half-life = 2 days (exponential decay)
```

## Example 10: Performance Metrics

```
Performance Test Results
========================

Configuration:
- Model: cardiffnlp/twitter-roberta-base-sentiment
- Device: CPU (Intel i7-9700K)
- Batch size: 1
- Test tweets: 100

Results:
--------
Tweet parsing:         0.8ms avg
Sentiment inference:   142ms avg
Result processing:     1.2ms avg
Total per tweet:       144ms avg

Throughput:            ~7 tweets/second
Memory usage:          623 MB
CPU usage:             45% (single core)

With GPU (NVIDIA RTX 3080):
---------------------------
Sentiment inference:   18ms avg
Total per tweet:       20ms avg
Throughput:            ~50 tweets/second
GPU memory:            512 MB
```

## Understanding the Metrics

### Weighted Score Scale
```
+1.00 to +0.70: Very Bullish  🚀🚀🚀
+0.69 to +0.30: Bullish       🚀🚀
+0.29 to +0.20: Slightly Bullish 🚀
+0.19 to -0.19: Neutral       ➡️
-0.20 to -0.29: Slightly Bearish 📉
-0.30 to -0.69: Bearish       📉📉
-0.70 to -1.00: Very Bearish  📉📉📉
```

### Confidence Levels
```
0.90 - 1.00: Very High (excellent signal)
0.75 - 0.89: High (reliable signal)
0.60 - 0.74: Medium (acceptable signal)
0.00 - 0.59: Low (filtered out by default)
```

### Sample Size Guidelines
```
< 5 tweets:    Insufficient data
5-10 tweets:   Minimal confidence
10-20 tweets:  Acceptable
20-50 tweets:  Good
> 50 tweets:   Excellent statistical significance
```

## Visualization Ideas

These examples can be used to create:

1. **Real-time Dashboard**: Show live tweet processing
2. **Sentiment Chart**: Line chart of weighted scores over time
3. **Heatmap**: Grid of tickers colored by sentiment
4. **Leaderboard**: Top bullish/bearish tickers
5. **Alert System**: Notify on significant sentiment changes

## Next Steps

- See [sentiment_example.py](src/sentiment_example.py) for runnable code
- Read [SENTIMENT_DOCUMENTATION.md](docs/SENTIMENT_DOCUMENTATION.md) for API details
- Try [SENTIMENT_QUICKSTART.md](SENTIMENT_QUICKSTART.md) to get started
