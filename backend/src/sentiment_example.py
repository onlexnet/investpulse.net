"""
Example usage of the sentiment analysis module.

This script demonstrates how to use the sentiment module to:
1. Monitor Twitter stream for financial news
2. Analyze sentiment of tweets
3. Calculate weighted sentiment scores for tickers
"""

import logging
import time
from src.sentiment import (
    SentimentConfig,
    TwitterStreamMonitor,
    SentimentAnalyzer,
    SentimentAggregator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_tweet(
    tweet_data,
    analyzer: SentimentAnalyzer,
    aggregator: SentimentAggregator
) -> None:
    """
    Process incoming tweet: analyze sentiment and aggregate results.
    
    Parameters:
        tweet_data: TweetData object from stream
        analyzer: SentimentAnalyzer instance
        aggregator: SentimentAggregator instance
    """
    # Analyze sentiment
    sentiment_result = analyzer.analyze(tweet_data)
    
    if sentiment_result and analyzer.is_high_confidence(sentiment_result):
        # Add to aggregation
        aggregator.add_sentiment_result(sentiment_result)
        
        logger.info(
            f"Processed tweet from @{tweet_data.author_username}: "
            f"{sentiment_result.sentiment.value} "
            f"(confidence: {sentiment_result.confidence:.3f}) "
            f"Tickers: {', '.join(tweet_data.mentioned_tickers)}"
        )


def main():
    """Main function to run sentiment analysis system."""
    
    # Create configuration (twitter_bearer_token will be loaded from TWITTER_BEARER_TOKEN env var)
    config = SentimentConfig(
        monitored_accounts=['Benzinga', 'fxhedgers', 'ZeroHedge', 'Finviz_com', 'FT'],
        target_tickers={'NVDA', 'MSFT', 'AAPL'},
        sentiment_window_days=5,
        min_confidence_threshold=0.6,
        use_gpu=False
    )
    
    logger.info("Initializing sentiment analysis system...")
    
    # Initialize components
    analyzer = SentimentAnalyzer(config)
    aggregator = SentimentAggregator(config)
    
    # Define callback for processing tweets
    def on_tweet(tweet_data):
        process_tweet(tweet_data, analyzer, aggregator)
    
    # Create Twitter stream monitor
    monitor = TwitterStreamMonitor(config, on_tweet_callback=on_tweet)
    
    logger.info("Starting Twitter stream monitoring...")
    logger.info(f"Monitoring accounts: {', '.join(config.monitored_accounts)}")
    logger.info(f"Target tickers: {', '.join(config.target_tickers)}")
    
    try:
        # Start monitoring (this is blocking)
        monitor.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        monitor.stop()
        
        # Print final weighted sentiments
        logger.info("\n=== Final Weighted Sentiments ===")
        weighted_sentiments = aggregator.get_all_weighted_sentiments()
        
        for ticker, sentiment in weighted_sentiments.items():
            logger.info(f"\n{ticker}:")
            logger.info(f"  Direction: {sentiment.sentiment_direction}")
            logger.info(f"  Weighted Score: {sentiment.weighted_score:.4f}")
            logger.info(f"  Total Tweets: {sentiment.total_tweets}")
            logger.info(f"  Average Confidence: {sentiment.average_confidence:.3f}")
            logger.info(
                f"  Weights - Positive: {sentiment.positive_weight:.2f}, "
                f"Negative: {sentiment.negative_weight:.2f}, "
                f"Neutral: {sentiment.neutral_weight:.2f}"
            )


def periodic_reporting_example():
    """
    Example of periodic sentiment reporting without stream monitoring.
    
    This demonstrates how to periodically check and report weighted sentiments.
    """
    config = SentimentConfig(
        target_tickers={'NVDA', 'MSFT', 'AAPL'},
        sentiment_window_days=5
    )
    
    aggregator = SentimentAggregator(config)
    
    # Simulate adding some sentiment results
    # (In practice, these would come from the Twitter stream)
    
    # Periodic reporting loop
    while True:
        time.sleep(300)  # Report every 5 minutes
        
        weighted_sentiments = aggregator.get_all_weighted_sentiments()
        
        logger.info("\n=== Periodic Sentiment Report ===")
        for ticker, sentiment in weighted_sentiments.items():
            logger.info(
                f"{ticker}: {sentiment.sentiment_direction} "
                f"(score: {sentiment.weighted_score:.4f}, "
                f"tweets: {sentiment.total_tweets})"
            )
        
        # Clean up old data
        aggregator.clear_old_sentiments()


if __name__ == "__main__":
    main()
