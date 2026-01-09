"""
Example: Running sentiment analysis with Ray actors.

This example demonstrates how to use the Ray-based distributed sentiment
analysis system with async Tweepy for non-blocking Twitter streaming.
"""

import asyncio
import logging
from src.sentiment import (
    SentimentConfig,
    SentimentOrchestrator,
    run_sentiment_pipeline
)
from src.sentiment.utils import format_sentiment_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_basic_orchestrator():
    """
    Example 1: Basic usage with SentimentOrchestrator actor.
    
    This example shows how to manually create and control the orchestrator.
    """
    import ray
    
    # Initialize Ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    
    # Create configuration
    config = SentimentConfig(
        twitter_bearer_token="your_token_here",
        target_tickers={"AAPL", "MSFT", "NVDA", "GOOGL"},
        monitored_accounts=["Benzinga", "fxhedgers", "ZeroHedge"],
        sentiment_window_days=7,
        use_gpu=False  # Set to True if GPU is available
    )
    
    # Create orchestrator actor with 3 parallel analyzers
    orchestrator = SentimentOrchestrator.remote(config, num_analyzers=3)
    
    try:
        # Initialize all child actors
        logger.info("Initializing child actors...")
        init_success = ray.get(orchestrator.initialize.remote())
        if not init_success:
            logger.error("Failed to initialize orchestrator")
            return
        
        # Start the pipeline
        logger.info("Starting sentiment pipeline...")
        start_success = ray.get(orchestrator.start.remote())
        if not start_success:
            logger.error("Failed to start pipeline")
            return
        
        # Run for 5 minutes, checking sentiments every minute
        for i in range(5):
            await asyncio.sleep(60)
            
            # Get current sentiments
            sentiments = ray.get(orchestrator.get_sentiments.remote())
            
            if isinstance(sentiments, dict) and sentiments:
                logger.info(f"\n--- Sentiment Report (minute {i+1}) ---")
                print(format_sentiment_report(sentiments))
            else:
                logger.info(f"No sentiments available yet (minute {i+1})")
        
        # Get final sentiments
        final_sentiments = ray.get(orchestrator.get_sentiments.remote())
        if isinstance(final_sentiments, dict):
            logger.info("\n=== Final Sentiment Report ===")
            print(format_sentiment_report(final_sentiments))
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        # Clean up
        ray.get(orchestrator.cleanup.remote())
        ray.kill(orchestrator)
        logger.info("Pipeline stopped and cleaned up")


async def example_simple_pipeline():
    """
    Example 2: Simple pipeline using run_sentiment_pipeline helper.
    
    This is the easiest way to run the sentiment pipeline.
    """
    # Create configuration
    config = SentimentConfig(
        twitter_bearer_token="your_token_here",
        target_tickers={"TSLA", "AAPL", "AMZN"},
        monitored_accounts=["Benzinga", "fxhedgers"],
        sentiment_window_days=5
    )
    
    # Run pipeline for 10 minutes (600 seconds)
    # Use num_analyzers=2 for 2 parallel sentiment analyzers
    final_sentiments = await run_sentiment_pipeline(
        config,
        duration_seconds=600,
        num_analyzers=2
    )
    
    # Print final results
    if final_sentiments:
        logger.info("\n=== Final Sentiment Report ===")
        print(format_sentiment_report(final_sentiments))
    else:
        logger.info("No sentiments collected")


async def example_continuous_monitoring():
    """
    Example 3: Continuous monitoring with periodic reporting.
    
    This example runs indefinitely and saves reports periodically.
    """
    import json
    from datetime import datetime
    import ray
    
    # Initialize Ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    
    # Create configuration
    config = SentimentConfig(
        twitter_bearer_token="your_token_here",
        target_tickers={"AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN"},
        monitored_accounts=["Benzinga", "fxhedgers", "ZeroHedge", "Finviz_com"],
        sentiment_window_days=7,
        use_gpu=True  # Use GPU for faster analysis
    )
    
    # Create orchestrator actor with 4 parallel analyzers for high throughput
    orchestrator = SentimentOrchestrator.remote(config, num_analyzers=4)
    
    try:
        # Initialize and start
        ray.get(orchestrator.initialize.remote())
        ray.get(orchestrator.start.remote())
        
        logger.info("Starting continuous monitoring (Ctrl+C to stop)...")
        
        # Run indefinitely
        iteration = 0
        while True:
            # Wait 10 minutes between reports
            await asyncio.sleep(600)
            iteration += 1
            
            # Get current sentiments
            sentiments = ray.get(orchestrator.get_sentiments.remote())
            
            if isinstance(sentiments, dict) and sentiments:
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"sentiment_report_{timestamp}.json"
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "iteration": iteration,
                    "sentiments": {
                        ticker: sentiment.to_dict()
                        for ticker, sentiment in sentiments.items()
                    }
                }
                
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Saved report to {output_file}")
                
                # Print summary
                print(f"\n--- Iteration {iteration} ---")
                print(format_sentiment_report(sentiments))
            else:
                logger.info(f"No sentiments available yet (iteration {iteration})")
    
    except KeyboardInterrupt:
        logger.info("Stopping continuous monitoring...")
    finally:
        ray.get(orchestrator.cleanup.remote())
        ray.kill(orchestrator)


async def example_get_specific_ticker():
    """
    Example 4: Query sentiment for a specific ticker.
    
    This example shows how to get sentiment for just one ticker.
    """
    import ray
    
    # Initialize Ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    
    config = SentimentConfig(
        twitter_bearer_token="your_token_here",
        target_tickers={"AAPL", "MSFT", "NVDA"},
    )
    
    orchestrator = SentimentOrchestrator.remote(config, num_analyzers=2)
    
    try:
        ray.get(orchestrator.initialize.remote())
        ray.get(orchestrator.start.remote())
        
        # Run for 3 minutes
        await asyncio.sleep(180)
        
        # Get sentiment for specific ticker
        ticker = "AAPL"
        sentiment = ray.get(orchestrator.get_sentiments.remote(ticker=ticker))
        
        if sentiment and not isinstance(sentiment, dict):
            logger.info(f"\nSentiment for {ticker}:")
            logger.info(f"  Direction: {sentiment.sentiment_direction}")
            logger.info(f"  Score: {sentiment.weighted_score:+.4f}")
            logger.info(f"  Tweets: {sentiment.total_tweets}")
            logger.info(f"  Confidence: {sentiment.average_confidence:.3f}")
        else:
            logger.info(f"No sentiment data available for {ticker}")
    
    finally:
        ray.get(orchestrator.cleanup.remote())
        ray.kill(orchestrator)


def main():
    """
    Main entry point - choose which example to run.
    """
    # Uncomment the example you want to run:
    
    # Example 1: Basic orchestrator usage
    # asyncio.run(example_basic_orchestrator())
    
    # Example 2: Simple pipeline helper
    # asyncio.run(example_simple_pipeline())
    
    # Example 3: Continuous monitoring
    # asyncio.run(example_continuous_monitoring())
    
    # Example 4: Query specific ticker
    asyncio.run(example_get_specific_ticker())


if __name__ == "__main__":
    main()
