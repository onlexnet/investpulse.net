"""
Simple test to verify TwitterStreamMonitor can receive real Twitter data.
"""

import os
import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock
import ray

from src.sentiment import SentimentConfig
from src.sentiment.twitter_stream import TwitterStreamMonitor
from src.sentiment.models import TweetData


@pytest.fixture(scope="module")
def ray_context():
    """Initialize Ray for tests."""
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
    yield


@pytest.fixture
def test_config():
    """Create minimal test configuration."""
    yield SentimentConfig(
        twitter_bearer_token="test_token",
        target_tickers={"AAPL", "MSFT"},
        monitored_accounts=["Benzinga"]
    )


@pytest.fixture
def real_config():
    """Create configuration with real Twitter credentials from environment."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN not set in environment")
    
    return SentimentConfig(
        twitter_bearer_token=bearer_token,
        target_tickers={"AAPL", "MSFT", "NVDA"},
        monitored_accounts=["Benzinga", "fxhedgers"]
    )


def create_realistic_tweet():
    """Create a mock tweet matching real Twitter API v2 structure."""
    tweet = MagicMock()
    tweet.id = 1590123456789012345
    tweet.text = "$AAPL stock surges after earnings beat!"
    tweet.created_at = datetime(2025, 11, 12, 10, 30, 0)
    
    # Real public_metrics structure from Twitter API v2
    tweet.public_metrics = {
        'retweet_count': 150,
        'like_count': 500,
        'reply_count': 30,
        'quote_count': 12
    }
    
    # Real author structure
    mock_author = MagicMock()
    mock_author.username = "Benzinga"
    mock_author.id = "123456"
    
    tweet.author = mock_author
    tweet.author_id = "123456"
    
    return tweet


def test_parse_real_twitter_data(ray_context, test_config):
    """
    Test that TwitterStreamMonitor can parse realistic Twitter data.
    
    This simulates receiving a tweet from Twitter's filtered stream API
    and verifies all data is correctly extracted.
    """
    # Create actor
    stream_actor = TwitterStreamMonitor.remote(test_config, analyzer_actor=None)
    
    # Create realistic tweet
    real_tweet = create_realistic_tweet()
    
    # Parse the tweet
    result = ray.get(stream_actor._parse_tweet.remote(real_tweet))
    
    # Verify all data was correctly extracted
    assert result is not None
    assert isinstance(result, TweetData)
    assert result.tweet_id == "1590123456789012345"
    assert "AAPL" in result.text
    assert "AAPL" in result.mentioned_tickers
    assert result.author_username == "Benzinga"
    assert result.retweet_count == 150
    assert result.like_count == 500
    assert result.engagement_score == 800.0  # (150 * 2) + (500 * 1)
    
    print(f"\n✓ Successfully parsed Twitter data:")
    print(f"  Tweet ID: {result.tweet_id}")
    print(f"  Author: @{result.author_username}")
    print(f"  Tickers: {result.mentioned_tickers}")
    print(f"  Engagement: {result.engagement_score}")
    
    # Cleanup
    ray.kill(stream_actor)


@ray.remote
class TweetCollector:
    """Actor to collect tweets received from stream."""
    def __init__(self):
        self.tweets = []
    
    async def analyze_tweet(self, tweet_data: TweetData):
        """Receive and store tweet data."""
        self.tweets.append(tweet_data)
        return True
    
    def get_tweets(self):
        """Return collected tweets."""
        return self.tweets
    
    def get_count(self):
        """Return number of tweets collected."""
        return len(self.tweets)

@pytest.mark.asyncio
async def test_aaaaa1():
    pass

def test_aaaa3(ray_context, real_config):
    print("Test aaaa3 wykonany!")
    assert True

@pytest.mark.asyncio
async def test_receive_real_twitter_data(ray_context, real_config):
    """
    Integration test: Connect to real Twitter API and receive actual tweets.
    
    Requirements:
    - Set TWITTER_BEARER_TOKEN environment variable
    - Twitter API v2 access with filtered stream permissions
    
    This test will:
    1. Create TwitterStreamMonitor actor
    2. Connect to real Twitter filtered stream
    3. Collect tweets for 30 seconds
    4. Verify at least one tweet was received
    
    Run with: pytest tests/sentiment/test_twitter_stream.py::test_receive_real_twitter_data -v -s
    """
    print("\n" + "="*60)
    print("REAL TWITTER API INTEGRATION TEST")
    print("="*60)
    print(f"Target tickers: {real_config.target_tickers}")
    print(f"Monitored accounts: {real_config.monitored_accounts}")
    print("\nConnecting to Twitter filtered stream...")
    
    # Create tweet collector actor
    collector = TweetCollector.remote()
    
    # Create stream monitor actor with collector
    stream_actor = TwitterStreamMonitor.remote(real_config, collector)
    
    try:
        # Start streaming in background
        print("Starting stream monitor...")
        stream_actor.start.remote()  # type: ignore
        
        # Wait for 30 seconds to collect tweets
        print("Listening for tweets (30 seconds)...")
        for i in range(6):
            await asyncio.sleep(5)
            count = ray.get(collector.get_count.remote())  # type: ignore
            print(f"  {(i+1)*5}s: {count} tweets received")
        
        # Check results
        tweets = ray.get(collector.get_tweets.remote())  # type: ignore
        
        print(f"\n{'='*60}")
        print(f"RESULTS: Received {len(tweets)} tweets")
        print(f"{'='*60}")
        
        if tweets:
            print("\nSample tweets:")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"\n{i}. @{tweet.author_username}:")
                print(f"   Text: {tweet.text[:80]}...")
                print(f"   Tickers: {tweet.mentioned_tickers}")
                print(f"   Engagement: {tweet.engagement_score}")
            
            # Verify we got real data
            assert len(tweets) > 0, "Should receive at least one tweet"
            
            # Verify tweet structure
            first_tweet = tweets[0]
            assert first_tweet.tweet_id is not None
            assert len(first_tweet.text) > 0
            assert first_tweet.author_username is not None
            assert len(first_tweet.mentioned_tickers) > 0
            assert first_tweet.engagement_score >= 0
            
            print(f"\n✓ Successfully received and parsed real Twitter data!")
        else:
            print("\n⚠ No tweets received during test period.")
            print("  This may be normal if there's low activity for monitored accounts.")
            raise ValueError(
                "No tweets received during test period"
            )
            # pytest.skip("No tweets received during test period")
            
    finally:
        # Cleanup
        print("\nStopping stream...")
        ray.get(stream_actor.stop.remote())  # type: ignore
        ray.kill(stream_actor)
        ray.kill(collector)
        print("Cleanup complete.")
