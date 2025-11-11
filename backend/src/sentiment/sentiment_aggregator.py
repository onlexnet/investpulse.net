"""
Sentiment aggregation and weighted scoring for tickers.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .config import SentimentConfig
from .models import (
    SentimentResult,
    SentimentLabel,
    TickerSentiment,
    WeightedSentiment
)

logger = logging.getLogger(__name__)


class SentimentAggregator:
    """
    Aggregate and calculate weighted sentiment scores for tickers.
    
    Calculates weighted sentiment based on:
    - Sentiment direction (positive, negative, neutral)
    - Confidence scores
    - Engagement metrics (retweets, likes)
    - Time decay over the analysis window
    """
    
    def __init__(self, config: SentimentConfig):
        """
        Initialize sentiment aggregator.
        
        Parameters:
            config: Sentiment analysis configuration
        """
        self.config = config
        # Storage for sentiment results by ticker
        self.sentiment_history: Dict[str, List[TickerSentiment]] = defaultdict(
            list
        )
    
    def add_sentiment_result(self, result: SentimentResult) -> None:
        """
        Add a sentiment result to the aggregation history.
        
        Parameters:
            result: Sentiment result to add
        """
        # Create ticker sentiments for each mentioned ticker
        for ticker in result.tweet_data.mentioned_tickers:
            ticker_sentiment = TickerSentiment(
                ticker=ticker,
                sentiment=result.sentiment,
                confidence=result.confidence,
                engagement_score=result.tweet_data.engagement_score,
                timestamp=result.tweet_data.created_at
            )
            
            self.sentiment_history[ticker].append(ticker_sentiment)
            
            logger.debug(
                f"Added sentiment for {ticker}: {result.sentiment.value} "
                f"(engagement: {ticker_sentiment.engagement_score:.1f})"
            )
    
    def _get_sentiment_numeric_value(self, sentiment: SentimentLabel) -> float:
        """
        Convert sentiment label to numeric value.
        
        Parameters:
            sentiment: Sentiment label
            
        Returns:
            Numeric value: 1.0 for positive, -1.0 for negative, 0.0 for neutral
        """
        mapping = {
            SentimentLabel.POSITIVE: 1.0,
            SentimentLabel.NEGATIVE: -1.0,
            SentimentLabel.NEUTRAL: 0.0
        }
        return mapping[sentiment]
    
    def _calculate_time_decay_weight(
        self,
        timestamp: datetime,
        current_time: datetime
    ) -> float:
        """
        Calculate time decay weight for a sentiment.
        
        More recent sentiments have higher weight. Uses exponential decay
        over the configured window period.
        
        Parameters:
            timestamp: When the sentiment was recorded
            current_time: Current reference time
            
        Returns:
            Weight multiplier (0.0 to 1.0)
        """
        # Calculate age in days
        age_delta = current_time - timestamp
        age_days = age_delta.total_seconds() / (24 * 3600)
        
        # Exponential decay with half-life of 2 days
        half_life = 2.0
        decay_factor = 0.5 ** (age_days / half_life)
        
        return max(0.0, min(1.0, decay_factor))
    
    def _calculate_weighted_score(
        self,
        sentiments: List[TickerSentiment],
        window_start: datetime,
        window_end: datetime
    ) -> tuple[float, float, float, float, float]:
        """
        Calculate weighted sentiment score for a ticker.
        
        Parameters:
            sentiments: List of ticker sentiments in the window
            window_start: Start of analysis window
            window_end: End of analysis window
            
        Returns:
            Tuple of (weighted_score, pos_weight, neg_weight, neu_weight,
                     avg_confidence)
        """
        positive_weight = 0.0
        negative_weight = 0.0
        neutral_weight = 0.0
        total_confidence = 0.0
        
        for sentiment in sentiments:
            # Calculate base weight from engagement and confidence
            engagement_weight = 1.0 + (sentiment.engagement_score / 100.0)
            confidence_weight = sentiment.confidence
            
            # Apply time decay
            time_weight = self._calculate_time_decay_weight(
                sentiment.timestamp,
                window_end
            )
            
            # Combined weight
            weight = engagement_weight * confidence_weight * time_weight
            
            # Get sentiment numeric value
            sentiment_value = self._get_sentiment_numeric_value(
                sentiment.sentiment
            )
            
            # Accumulate weights by sentiment type
            if sentiment.sentiment == SentimentLabel.POSITIVE:
                positive_weight += weight
            elif sentiment.sentiment == SentimentLabel.NEGATIVE:
                negative_weight += weight
            else:
                neutral_weight += weight
            
            total_confidence += sentiment.confidence
        
        # Calculate overall weighted score
        total_weight = positive_weight + negative_weight + neutral_weight
        
        if total_weight > 0:
            weighted_score = (
                (positive_weight - negative_weight) / total_weight
            )
        else:
            weighted_score = 0.0
        
        # Calculate average confidence
        avg_confidence = (
            total_confidence / len(sentiments) if sentiments else 0.0
        )
        
        return (
            weighted_score,
            positive_weight,
            negative_weight,
            neutral_weight,
            avg_confidence
        )
    
    def get_weighted_sentiment(
        self,
        ticker: str,
        window_end: Optional[datetime] = None
    ) -> Optional[WeightedSentiment]:
        """
        Calculate weighted sentiment for a ticker over the configured window.
        
        Parameters:
            ticker: Stock ticker symbol
            window_end: End of analysis window (default: now)
            
        Returns:
            WeightedSentiment object or None if insufficient data
        """
        if ticker not in self.sentiment_history:
            logger.warning(f"No sentiment history for ticker {ticker}")
            return None
        
        # Set window boundaries
        if window_end is None:
            window_end = datetime.now()
        
        window_start = window_end - timedelta(
            days=self.config.sentiment_window_days
        )
        
        # Filter sentiments within window
        sentiments_in_window = [
            s for s in self.sentiment_history[ticker]
            if window_start <= s.timestamp <= window_end
        ]
        
        if not sentiments_in_window:
            logger.warning(
                f"No sentiments for {ticker} in window "
                f"{window_start} to {window_end}"
            )
            return None
        
        # Calculate weighted scores
        (
            weighted_score,
            pos_weight,
            neg_weight,
            neu_weight,
            avg_confidence
        ) = self._calculate_weighted_score(
            sentiments_in_window,
            window_start,
            window_end
        )
        
        # Create weighted sentiment result
        result = WeightedSentiment(
            ticker=ticker,
            weighted_score=weighted_score,
            positive_weight=pos_weight,
            negative_weight=neg_weight,
            neutral_weight=neu_weight,
            total_tweets=len(sentiments_in_window),
            window_start=window_start,
            window_end=window_end,
            average_confidence=avg_confidence
        )
        
        logger.info(
            f"Weighted sentiment for {ticker}: {weighted_score:.4f} "
            f"({result.sentiment_direction}) from {len(sentiments_in_window)} "
            f"tweets"
        )
        
        return result
    
    def get_all_weighted_sentiments(
        self,
        window_end: Optional[datetime] = None
    ) -> Dict[str, WeightedSentiment]:
        """
        Calculate weighted sentiments for all tracked tickers.
        
        Parameters:
            window_end: End of analysis window (default: now)
            
        Returns:
            Dictionary mapping tickers to their weighted sentiments
        """
        results = {}
        
        for ticker in self.sentiment_history.keys():
            weighted_sentiment = self.get_weighted_sentiment(ticker, window_end)
            if weighted_sentiment:
                results[ticker] = weighted_sentiment
        
        logger.info(
            f"Calculated weighted sentiments for {len(results)} tickers"
        )
        
        return results
    
    def clear_old_sentiments(self, cutoff_date: Optional[datetime] = None) -> int:
        """
        Remove sentiment data older than cutoff date to free memory.
        
        Parameters:
            cutoff_date: Remove sentiments older than this date
                        (default: window_days * 2 ago)
            
        Returns:
            Number of sentiments removed
        """
        if cutoff_date is None:
            cutoff_date = datetime.now() - timedelta(
                days=self.config.sentiment_window_days * 2
            )
        
        removed_count = 0
        
        for ticker in list(self.sentiment_history.keys()):
            original_count = len(self.sentiment_history[ticker])
            
            # Keep only recent sentiments
            self.sentiment_history[ticker] = [
                s for s in self.sentiment_history[ticker]
                if s.timestamp >= cutoff_date
            ]
            
            removed_count += (
                original_count - len(self.sentiment_history[ticker])
            )
            
            # Remove ticker if no sentiments remain
            if not self.sentiment_history[ticker]:
                del self.sentiment_history[ticker]
        
        logger.info(f"Removed {removed_count} old sentiments (before {cutoff_date})")
        
        return removed_count
