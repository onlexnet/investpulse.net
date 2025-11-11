"""
Sentiment analysis module for Twitter financial news.

This module provides functionality to:
- Monitor Twitter filtered stream API for financial news accounts
- Analyze sentiment of posts related to specific tickers
- Calculate weighted sentiment scores based on engagement metrics
"""

from .twitter_stream import TwitterStreamMonitor
from .sentiment_analyzer import SentimentAnalyzer
from .sentiment_aggregator import SentimentAggregator
from .models import (
    TweetData,
    SentimentResult,
    WeightedSentiment,
    SentimentLabel,
    TickerSentiment
)
from .config import SentimentConfig
from . import utils

__all__ = [
    'TwitterStreamMonitor',
    'SentimentAnalyzer',
    'SentimentAggregator',
    'TweetData',
    'SentimentResult',
    'WeightedSentiment',
    'SentimentLabel',
    'TickerSentiment',
    'SentimentConfig',
    'utils',
]
