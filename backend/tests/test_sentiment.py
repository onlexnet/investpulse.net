"""
Unit tests for sentiment analysis module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.sentiment.config import SentimentConfig
from src.sentiment.models import (
    TweetData,
    SentimentResult,
    SentimentLabel,
    TickerSentiment,
    WeightedSentiment
)
from src.sentiment.sentiment_aggregator import SentimentAggregator


class TestSentimentConfig:
    """Tests for SentimentConfig class."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = SentimentConfig()
        
        assert 'Benzinga' in config.monitored_accounts
        assert 'NVDA' in config.target_tickers
        assert config.sentiment_window_days == 5
        assert config.min_confidence_threshold == 0.6
    
    def test_add_ticker(self):
        """Test adding a ticker to configuration."""
        config = SentimentConfig()
        config.add_ticker('TSLA')
        
        assert 'TSLA' in config.target_tickers
    
    def test_add_ticker_lowercase_converts_to_uppercase(self):
        """Test that lowercase ticker is converted to uppercase."""
        config = SentimentConfig()
        config.add_ticker('googl')
        
        assert 'GOOGL' in config.target_tickers
    
    def test_remove_ticker(self):
        """Test removing a ticker from configuration."""
        config = SentimentConfig()
        config.add_ticker('TSLA')
        config.remove_ticker('TSLA')
        
        assert 'TSLA' not in config.target_tickers
    
    def test_add_account(self):
        """Test adding an account to monitoring list."""
        config = SentimentConfig()
        config.add_account('WSJ')
        
        assert 'WSJ' in config.monitored_accounts
    
    def test_add_account_with_at_symbol(self):
        """Test adding account with @ symbol strips it."""
        config = SentimentConfig()
        config.add_account('@BloombergMarkets')
        
        assert 'BloombergMarkets' in config.monitored_accounts
    
    def test_remove_account(self):
        """Test removing an account from monitoring list."""
        config = SentimentConfig()
        config.remove_account('Benzinga')
        
        assert 'Benzinga' not in config.monitored_accounts


class TestTweetData:
    """Tests for TweetData model."""
    
    def test_engagement_score_calculation(self):
        """Test engagement score is calculated correctly."""
        tweet = TweetData(
            tweet_id="123",
            text="Test tweet",
            author_username="test_user",
            created_at=datetime.now(),
            retweet_count=10,
            like_count=50,
            mentioned_tickers=['NVDA']
        )
        
        # Engagement = retweets * 2 + likes * 1
        expected_score = 10 * 2.0 + 50 * 1.0
        assert tweet.engagement_score == expected_score
    
    def test_zero_engagement(self):
        """Test tweet with zero engagement."""
        tweet = TweetData(
            tweet_id="123",
            text="Test tweet",
            author_username="test_user",
            created_at=datetime.now(),
            mentioned_tickers=['NVDA']
        )
        
        assert tweet.engagement_score == 0.0


class TestSentimentResult:
    """Tests for SentimentResult model."""
    
    def test_is_reliable_above_threshold(self):
        """Test is_reliable returns True for high confidence."""
        tweet = TweetData(
            tweet_id="123",
            text="Test tweet",
            author_username="test_user",
            created_at=datetime.now(),
            mentioned_tickers=['NVDA']
        )
        
        result = SentimentResult(
            tweet_data=tweet,
            sentiment=SentimentLabel.POSITIVE,
            confidence=0.8,
            scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
        )
        
        assert result.is_reliable is True
    
    def test_is_reliable_below_threshold(self):
        """Test is_reliable returns False for low confidence."""
        tweet = TweetData(
            tweet_id="123",
            text="Test tweet",
            author_username="test_user",
            created_at=datetime.now(),
            mentioned_tickers=['NVDA']
        )
        
        result = SentimentResult(
            tweet_data=tweet,
            sentiment=SentimentLabel.NEUTRAL,
            confidence=0.4,
            scores={'positive': 0.3, 'negative': 0.3, 'neutral': 0.4}
        )
        
        assert result.is_reliable is False


class TestWeightedSentiment:
    """Tests for WeightedSentiment model."""
    
    def test_sentiment_direction_bullish(self):
        """Test sentiment direction for positive score."""
        sentiment = WeightedSentiment(
            ticker='NVDA',
            weighted_score=0.5,
            positive_weight=10.0,
            negative_weight=5.0,
            neutral_weight=2.0,
            total_tweets=10,
            window_start=datetime.now() - timedelta(days=5),
            window_end=datetime.now(),
            average_confidence=0.75
        )
        
        assert sentiment.sentiment_direction == "BULLISH"
    
    def test_sentiment_direction_bearish(self):
        """Test sentiment direction for negative score."""
        sentiment = WeightedSentiment(
            ticker='NVDA',
            weighted_score=-0.5,
            positive_weight=5.0,
            negative_weight=10.0,
            neutral_weight=2.0,
            total_tweets=10,
            window_start=datetime.now() - timedelta(days=5),
            window_end=datetime.now(),
            average_confidence=0.75
        )
        
        assert sentiment.sentiment_direction == "BEARISH"
    
    def test_sentiment_direction_neutral(self):
        """Test sentiment direction for near-zero score."""
        sentiment = WeightedSentiment(
            ticker='NVDA',
            weighted_score=0.1,
            positive_weight=5.0,
            negative_weight=4.5,
            neutral_weight=5.0,
            total_tweets=10,
            window_start=datetime.now() - timedelta(days=5),
            window_end=datetime.now(),
            average_confidence=0.75
        )
        
        assert sentiment.sentiment_direction == "NEUTRAL"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        sentiment = WeightedSentiment(
            ticker='NVDA',
            weighted_score=0.5,
            positive_weight=10.0,
            negative_weight=5.0,
            neutral_weight=2.0,
            total_tweets=10,
            window_start=datetime.now() - timedelta(days=5),
            window_end=datetime.now(),
            average_confidence=0.75
        )
        
        data = sentiment.to_dict()
        
        assert data['ticker'] == 'NVDA'
        assert data['sentiment_direction'] == 'BULLISH'
        assert 'weighted_score' in data
        assert 'total_tweets' in data


class TestSentimentAggregator:
    """Tests for SentimentAggregator class."""
    
    def test_add_sentiment_result(self):
        """Test adding sentiment results to aggregator."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        tweet = TweetData(
            tweet_id="123",
            text="Test tweet",
            author_username="test_user",
            created_at=datetime.now(),
            retweet_count=10,
            like_count=50,
            mentioned_tickers=['NVDA', 'MSFT']
        )
        
        result = SentimentResult(
            tweet_data=tweet,
            sentiment=SentimentLabel.POSITIVE,
            confidence=0.8,
            scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
        )
        
        aggregator.add_sentiment_result(result)
        
        assert len(aggregator.sentiment_history['NVDA']) == 1
        assert len(aggregator.sentiment_history['MSFT']) == 1
    
    def test_get_sentiment_numeric_value(self):
        """Test conversion of sentiment labels to numeric values."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        assert aggregator._get_sentiment_numeric_value(
            SentimentLabel.POSITIVE
        ) == 1.0
        assert aggregator._get_sentiment_numeric_value(
            SentimentLabel.NEGATIVE
        ) == -1.0
        assert aggregator._get_sentiment_numeric_value(
            SentimentLabel.NEUTRAL
        ) == 0.0
    
    def test_time_decay_weight(self):
        """Test time decay weight calculation."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        current_time = datetime.now()
        
        # Recent tweet should have high weight
        recent_weight = aggregator._calculate_time_decay_weight(
            current_time - timedelta(hours=1),
            current_time
        )
        assert recent_weight > 0.9
        
        # Old tweet should have lower weight
        old_weight = aggregator._calculate_time_decay_weight(
            current_time - timedelta(days=4),
            current_time
        )
        assert old_weight < 0.5
    
    def test_get_weighted_sentiment_no_data(self):
        """Test getting weighted sentiment with no data."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        result = aggregator.get_weighted_sentiment('NVDA')
        
        assert result is None
    
    def test_get_weighted_sentiment_with_data(self):
        """Test calculating weighted sentiment with data."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        # Add multiple sentiment results
        for i in range(5):
            tweet = TweetData(
                tweet_id=str(i),
                text=f"Test tweet {i}",
                author_username="test_user",
                created_at=datetime.now() - timedelta(days=i),
                retweet_count=10,
                like_count=50,
                mentioned_tickers=['NVDA']
            )
            
            result = SentimentResult(
                tweet_data=tweet,
                sentiment=SentimentLabel.POSITIVE,
                confidence=0.8,
                scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
            )
            
            aggregator.add_sentiment_result(result)
        
        weighted = aggregator.get_weighted_sentiment('NVDA')
        
        assert weighted is not None
        assert weighted.ticker == 'NVDA'
        assert weighted.total_tweets == 5
        assert weighted.weighted_score > 0  # Should be positive
        assert weighted.sentiment_direction == 'BULLISH'
    
    def test_get_all_weighted_sentiments(self):
        """Test getting weighted sentiments for all tickers."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        # Add data for multiple tickers
        for ticker in ['NVDA', 'MSFT', 'AAPL']:
            tweet = TweetData(
                tweet_id=ticker,
                text=f"Test tweet about {ticker}",
                author_username="test_user",
                created_at=datetime.now(),
                retweet_count=10,
                like_count=50,
                mentioned_tickers=[ticker]
            )
            
            result = SentimentResult(
                tweet_data=tweet,
                sentiment=SentimentLabel.POSITIVE,
                confidence=0.8,
                scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
            )
            
            aggregator.add_sentiment_result(result)
        
        all_sentiments = aggregator.get_all_weighted_sentiments()
        
        assert len(all_sentiments) == 3
        assert 'NVDA' in all_sentiments
        assert 'MSFT' in all_sentiments
        assert 'AAPL' in all_sentiments
    
    def test_clear_old_sentiments(self):
        """Test clearing old sentiment data."""
        config = SentimentConfig()
        aggregator = SentimentAggregator(config)
        
        # Add old sentiment
        old_tweet = TweetData(
            tweet_id="old",
            text="Old tweet",
            author_username="test_user",
            created_at=datetime.now() - timedelta(days=20),
            mentioned_tickers=['NVDA']
        )
        
        old_result = SentimentResult(
            tweet_data=old_tweet,
            sentiment=SentimentLabel.POSITIVE,
            confidence=0.8,
            scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
        )
        
        aggregator.add_sentiment_result(old_result)
        
        # Add recent sentiment
        recent_tweet = TweetData(
            tweet_id="recent",
            text="Recent tweet",
            author_username="test_user",
            created_at=datetime.now(),
            mentioned_tickers=['NVDA']
        )
        
        recent_result = SentimentResult(
            tweet_data=recent_tweet,
            sentiment=SentimentLabel.POSITIVE,
            confidence=0.8,
            scores={'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
        )
        
        aggregator.add_sentiment_result(recent_result)
        
        # Clear old sentiments (older than 10 days)
        cutoff = datetime.now() - timedelta(days=10)
        removed = aggregator.clear_old_sentiments(cutoff)
        
        assert removed == 1
        assert len(aggregator.sentiment_history['NVDA']) == 1


class TestSentimentIntegration:
    """Integration tests for sentiment analysis system."""
    
    def test_sentiment_analysis_returns_data(self):
        """Test that sentiment analysis returns data when processing tweets."""
        # Create configuration with mock token
        config = SentimentConfig(
            target_tickers={'NVDA', 'MSFT'},
            min_confidence_threshold=0.6
        )
        
        # Mock the analyzer's pipeline
        from src.sentiment.sentiment_analyzer import SentimentAnalyzer
        
        with patch.object(SentimentAnalyzer, '__init__', lambda self, config: None):
            analyzer = SentimentAnalyzer(config)
            analyzer.config = config
            
            # Mock the pipeline call
            mock_pipeline = MagicMock()
            mock_pipeline.return_value = [[
                {'label': 'LABEL_0', 'score': 0.05},
                {'label': 'LABEL_1', 'score': 0.10},
                {'label': 'LABEL_2', 'score': 0.85}
            ]]
            analyzer.pipeline = mock_pipeline
            
            # Mock label mapping
            analyzer.label_mapping = {
                "LABEL_0": SentimentLabel.NEGATIVE,
                "LABEL_1": SentimentLabel.NEUTRAL,
                "LABEL_2": SentimentLabel.POSITIVE
            }
            
            # Create test tweet data
            tweet = TweetData(
                tweet_id="test_123",
                text="NVDA stock is performing excellently! Great earnings report.",
                author_username="test_trader",
                created_at=datetime.now(),
                retweet_count=100,
                like_count=500,
                mentioned_tickers=['NVDA']
            )
            
            # Analyze sentiment
            result = analyzer.analyze(tweet)
            
            # Verify data is returned
            assert result is not None, "Sentiment analysis should return data"
            assert isinstance(result, SentimentResult), "Result should be SentimentResult instance"
            assert result.sentiment == SentimentLabel.POSITIVE, "Should detect positive sentiment"
            assert result.confidence > 0.8, "Should have high confidence"
            assert result.tweet_data == tweet, "Should include original tweet data"
        
    def test_aggregator_returns_weighted_sentiment_data(self):
        """Test that aggregator returns weighted sentiment data."""
        from src.sentiment.sentiment_analyzer import SentimentAnalyzer
        
        # Create configuration
        config = SentimentConfig(
            target_tickers={'AAPL'},
            sentiment_window_days=5,
            min_confidence_threshold=0.6
        )
        
        # Initialize components
        aggregator = SentimentAggregator(config)
        
        # Create mock analyzer
        with patch.object(SentimentAnalyzer, '__init__', lambda self, config: None):
            analyzer = SentimentAnalyzer(config)
            analyzer.config = config
            
            # Mock the pipeline
            mock_pipeline = MagicMock()
            mock_pipeline.return_value = [[
                {'label': 'LABEL_0', 'score': 0.05},
                {'label': 'LABEL_1', 'score': 0.10},
                {'label': 'LABEL_2', 'score': 0.85}
            ]]
            analyzer.pipeline = mock_pipeline
            
            # Mock label mapping
            analyzer.label_mapping = {
                "LABEL_0": SentimentLabel.NEGATIVE,
                "LABEL_1": SentimentLabel.NEUTRAL,
                "LABEL_2": SentimentLabel.POSITIVE
            }
            
            # Create and process multiple tweets
            for i in range(3):
                tweet = TweetData(
                    tweet_id=f"test_{i}",
                    text=f"AAPL stock analysis tweet {i}",
                    author_username="financial_news",
                    created_at=datetime.now() - timedelta(hours=i),
                    retweet_count=50 + i * 10,
                    like_count=200 + i * 50,
                    mentioned_tickers=['AAPL']
                )
                
                result = analyzer.analyze(tweet)
                if result:
                    aggregator.add_sentiment_result(result)
            
            # Get weighted sentiment
            weighted_sentiments = aggregator.get_all_weighted_sentiments()
            
            # Verify data is returned
            assert len(weighted_sentiments) > 0, "Should return weighted sentiment data"
            assert 'AAPL' in weighted_sentiments, "Should have AAPL sentiment"
            
            aapl_sentiment = weighted_sentiments['AAPL']
            assert isinstance(aapl_sentiment, WeightedSentiment), "Should be WeightedSentiment instance"
            assert aapl_sentiment.ticker == 'AAPL', "Ticker should match"
            assert aapl_sentiment.total_tweets == 3, "Should track all processed tweets"
            assert aapl_sentiment.weighted_score != 0, "Should calculate weighted score"
            assert aapl_sentiment.average_confidence > 0, "Should have average confidence"
        
    def test_config_loads_from_environment_variable(self):
        """Test that configuration loads TWITTER_BEARER_TOKEN from environment."""
        import os
        
        # Set environment variable
        test_token = "test_bearer_token_12345"
        with patch.dict(os.environ, {'TWITTER_BEARER_TOKEN': test_token}):
            # Create config without explicitly passing token
            config = SentimentConfig()
            
            # Verify token was loaded from environment
            assert config.twitter_bearer_token == test_token, "Should load token from environment variable"
        
        # Test with no environment variable
        with patch.dict(os.environ, {}, clear=True):
            config = SentimentConfig()
            assert config.twitter_bearer_token == "", "Should default to empty string when env var not set"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
