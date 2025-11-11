"""
Data models for sentiment analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class TweetData:
    """
    Represents a tweet from the filtered stream.
    
    Attributes:
        tweet_id: Unique identifier for the tweet
        text: Tweet content
        author_username: Username of the tweet author
        created_at: Timestamp when tweet was created
        retweet_count: Number of retweets
        like_count: Number of likes
        mentioned_tickers: List of stock tickers mentioned in the tweet
    """
    
    tweet_id: str
    text: str
    author_username: str
    created_at: datetime
    retweet_count: int = 0
    like_count: int = 0
    mentioned_tickers: list[str] = field(default_factory=list)
    
    @property
    def engagement_score(self) -> float:
        """
        Calculate engagement score based on retweets and likes.
        
        Returns:
            Combined engagement score (retweets weighted 2x, likes weighted 1x)
        """
        return (self.retweet_count * 2.0) + (self.like_count * 1.0)


@dataclass
class SentimentResult:
    """
    Results of sentiment analysis for a tweet.
    
    Attributes:
        tweet_data: Original tweet data
        sentiment: Sentiment label (positive, negative, neutral)
        confidence: Confidence score for the sentiment (0.0 to 1.0)
        scores: Dictionary of raw scores for each sentiment class
        analyzed_at: Timestamp when analysis was performed
    """
    
    tweet_data: TweetData
    sentiment: SentimentLabel
    confidence: float
    scores: Dict[str, float]
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_reliable(self) -> bool:
        """
        Check if sentiment analysis is reliable based on confidence threshold.
        
        Returns:
            True if confidence is above 0.6, False otherwise
        """
        return self.confidence >= 0.6


@dataclass
class TickerSentiment:
    """
    Sentiment data for a specific ticker from a single tweet.
    
    Attributes:
        ticker: Stock ticker symbol
        sentiment: Sentiment label
        confidence: Confidence score
        engagement_score: Tweet engagement score
        timestamp: When the tweet was created
    """
    
    ticker: str
    sentiment: SentimentLabel
    confidence: float
    engagement_score: float
    timestamp: datetime


@dataclass
class WeightedSentiment:
    """
    Aggregated weighted sentiment for a ticker over a time period.
    
    Attributes:
        ticker: Stock ticker symbol
        weighted_score: Weighted sentiment score (-1.0 to 1.0)
        positive_weight: Total weight of positive sentiments
        negative_weight: Total weight of negative sentiments
        neutral_weight: Total weight of neutral sentiments
        total_tweets: Number of tweets analyzed
        window_start: Start of analysis window
        window_end: End of analysis window
        average_confidence: Average confidence score across all tweets
    """
    
    ticker: str
    weighted_score: float
    positive_weight: float
    negative_weight: float
    neutral_weight: float
    total_tweets: int
    window_start: datetime
    window_end: datetime
    average_confidence: float
    
    @property
    def sentiment_direction(self) -> str:
        """
        Determine overall sentiment direction based on weighted score.
        
        Returns:
            String representation: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        if self.weighted_score > 0.2:
            return "BULLISH"
        elif self.weighted_score < -0.2:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def to_dict(self) -> Dict:
        """
        Convert weighted sentiment to dictionary format.
        
        Returns:
            Dictionary representation of weighted sentiment
        """
        return {
            'ticker': self.ticker,
            'weighted_score': round(self.weighted_score, 4),
            'sentiment_direction': self.sentiment_direction,
            'positive_weight': round(self.positive_weight, 4),
            'negative_weight': round(self.negative_weight, 4),
            'neutral_weight': round(self.neutral_weight, 4),
            'total_tweets': self.total_tweets,
            'average_confidence': round(self.average_confidence, 4),
            'window_start': self.window_start.isoformat(),
            'window_end': self.window_end.isoformat()
        }
