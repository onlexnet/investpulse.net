# Sentiment Analysis with Ray Actors - Migration Guide

## Overview

The sentiment analysis module has been migrated from blocking synchronous code to **asynchronous Ray actors** for distributed, non-blocking processing. This provides:

✅ **Non-blocking Twitter stream** - Async processing doesn't block the main thread  
✅ **Distributed sentiment analysis** - Multiple Ray actors process tweets in parallel  
✅ **Scalable architecture** - Easy to scale up/down the number of analyzer actors  
✅ **Centralized state management** - Single aggregator actor maintains sentiment history  
✅ **Better resource utilization** - Ray handles actor scheduling and resource allocation

## Architecture

### Ray Actor System

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              SentimentOrchestrator                  │
│         (Coordinates all actors)                    │
│                                                     │
└──────────┬──────────────────────┬──────────────────┘
           │                      │
           │                      │
    ┌──────▼─────────┐    ┌──────▼──────────────────┐
    │                │    │                         │
    │ TwitterStream  │    │  SentimentAggregator   │
    │    Monitor     │    │   (Stateful Actor)     │
    │  (Async Actor) │    │                         │
    │                │    │  - Stores sentiments    │
    └───────┬────────┘    │  - Calculates weights   │
            │             │  - Provides queries     │
            │ tweets      │                         │
            │             └─────────▲───────────────┘
            │                       │
            ▼                       │ results
    ┌───────────────┐              │
    │  Analyzer #1  ├──────────────┘
    │  (Ray Actor)  │
    └───────────────┘
    ┌───────────────┐
    │  Analyzer #2  ├──────────────┐
    │  (Ray Actor)  │              │
    └───────────────┘              │
    ┌───────────────┐              │
    │  Analyzer #N  ├──────────────┘
    │  (Ray Actor)  │
    └───────────────┘
```

## Key Changes

### 1. Twitter Stream Monitor (`TwitterStreamMonitor`)

**Before:**
```python
monitor = TwitterStreamMonitor(config, on_tweet_callback)
monitor.start()  # Blocking call
```

**After:**
```python
# Now it's a Ray actor
monitor = TwitterStreamMonitor.remote(config, analyzer_actor)
await monitor.start.remote()  # Non-blocking async
```

**Changes:**
- Now decorated with `@ray.remote`
- Takes `analyzer_actor` instead of callback
- `start()` is async and runs stream in executor
- Tweets are sent directly to analyzer actors
- Added `is_running()` method for status checks

### 2. Sentiment Analyzer (`SentimentAnalyzer`)

**Before:**
```python
analyzer = SentimentAnalyzer(config)
result = analyzer.analyze(tweet_data)  # Blocking
```

**After:**
```python
# Now it's a Ray actor
analyzer = SentimentAnalyzer.remote(config, aggregator_actor)
result = await analyzer.analyze_tweet.remote(tweet_data)  # Async
```

**Changes:**
- Now decorated with `@ray.remote`
- Takes `aggregator_actor` reference
- New async method `analyze_tweet()`
- Automatically sends results to aggregator
- Can run multiple instances in parallel
- Model inference runs in executor (non-blocking)

### 3. Sentiment Aggregator (`SentimentAggregator`)

**Before:**
```python
aggregator = SentimentAggregator(config)
aggregator.add_sentiment_result(result)
sentiments = aggregator.get_all_weighted_sentiments()
```

**After:**
```python
# Now it's a Ray actor
aggregator = SentimentAggregator.remote(config)
await aggregator.add_sentiment.remote(result)  # Async
sentiments = await aggregator.get_all_weighted_sentiments_async.remote()
```

**Changes:**
- Now decorated with `@ray.remote`
- New async methods: `add_sentiment()`, `get_weighted_sentiment_async()`, `get_all_weighted_sentiments_async()`
- Maintains state across all requests
- Single instance serves all analyzer actors
- Backward compatible sync methods still available

### 4. New Orchestrator (`SentimentOrchestrator`)

**New component** - Coordinates all Ray actors:

```python
orchestrator = SentimentOrchestrator(config, num_analyzers=3)
await orchestrator.initialize()  # Create all actors
await orchestrator.start()       # Start the pipeline
sentiments = await orchestrator.get_sentiments()  # Query results
orchestrator.cleanup()           # Clean up resources
```

**Features:**
- Automatic Ray initialization
- Creates and manages all actors
- Configurable number of parallel analyzers
- Simple query interface
- Proper cleanup and resource management

## Usage Examples

### Basic Usage

```python
import asyncio
from src.sentiment import SentimentConfig, SentimentOrchestrator

async def main():
    config = SentimentConfig(
        twitter_bearer_token="your_token",
        target_tickers={"AAPL", "MSFT", "NVDA"},
        monitored_accounts=["Benzinga", "fxhedgers"],
    )
    
    orchestrator = SentimentOrchestrator(config, num_analyzers=2)
    
    try:
        await orchestrator.initialize()
        await orchestrator.start()
        
        # Run for 5 minutes
        await asyncio.sleep(300)
        
        # Get results
        sentiments = await orchestrator.get_sentiments()
        print(sentiments)
    finally:
        orchestrator.cleanup()

asyncio.run(main())
```

### Using the Helper Function

```python
from src.sentiment import SentimentConfig, run_sentiment_pipeline

async def main():
    config = SentimentConfig(
        twitter_bearer_token="your_token",
        target_tickers={"TSLA", "AAPL"},
    )
    
    # Run for 10 minutes with 3 parallel analyzers
    sentiments = await run_sentiment_pipeline(
        config,
        duration_seconds=600,
        num_analyzers=3
    )
    
    print(sentiments)

asyncio.run(main())
```

### Query Specific Ticker

```python
# Get sentiment for specific ticker
sentiment = await orchestrator.get_sentiments(ticker="AAPL")
print(f"AAPL sentiment: {sentiment.weighted_score}")
```

## Configuration

### Number of Analyzers

Choose based on your workload:

- **Low volume (< 10 tweets/min)**: 1-2 analyzers
- **Medium volume (10-50 tweets/min)**: 2-4 analyzers
- **High volume (> 50 tweets/min)**: 4-8 analyzers

```python
orchestrator = SentimentOrchestrator(config, num_analyzers=4)
```

### GPU Support

Enable GPU for faster sentiment analysis:

```python
config = SentimentConfig(
    use_gpu=True,  # Enable GPU acceleration
    # ... other settings
)
```

## Migration Checklist

If you're updating existing code:

- [ ] Update imports to include `SentimentOrchestrator`, `run_sentiment_pipeline`
- [ ] Replace blocking calls with async/await
- [ ] Use `SentimentOrchestrator` instead of manual actor creation
- [ ] Update callback-based code to use actor message passing
- [ ] Add proper cleanup with `orchestrator.cleanup()`
- [ ] Test with different numbers of analyzer actors
- [ ] Update error handling for async code

## Performance Tips

1. **Scale analyzers based on load**: Monitor tweet volume and adjust `num_analyzers`
2. **Use GPU when available**: Set `use_gpu=True` for 2-3x faster analysis
3. **Batch queries**: Get all sentiments at once instead of querying each ticker
4. **Periodic cleanup**: Call `clear_old_sentiments()` on aggregator to free memory
5. **Ray dashboard**: Use Ray's dashboard to monitor actor performance

## Troubleshooting

### Ray not initialized
```python
# Ray auto-initializes, but you can do it manually:
import ray
ray.init(ignore_reinit_error=True)
```

### Actors not responding
```python
# Check if actor is alive
ray.get(actor.is_running.remote())
```

### Memory issues with long-running pipelines
```python
# Periodically clean old sentiments
await aggregator.clear_old_sentiments.remote()
```

### Stream connection issues
```python
# Monitor stream actor status
is_running = ray.get(stream_actor.is_running.remote())
if not is_running:
    # Restart the stream
    await stream_actor.start.remote()
```

## API Reference

See example file: `src/sentiment_ray_example.py` for complete working examples.

### Key Methods

**SentimentOrchestrator:**
- `initialize()` - Create all Ray actors
- `start()` - Start the pipeline
- `stop()` - Stop the pipeline
- `get_sentiments(ticker=None)` - Query sentiment data
- `cleanup()` - Clean up resources

**Actors:**
- All actors support `.remote()` for async execution
- Use `ray.get()` for blocking results
- Use `await` for async results

## Dependencies

New dependencies added to `requirements.txt`:
- `async-tweepy>=0.1.0` - Async Twitter API support
- `aiohttp>=3.9.0` - Async HTTP client
- `ray[default]` - Already included

## See Also

- `src/sentiment_ray_example.py` - Complete examples
- `src/sentiment/ray_orchestrator.py` - Orchestrator implementation
- Ray documentation: https://docs.ray.io/
