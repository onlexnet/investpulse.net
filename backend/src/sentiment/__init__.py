"""
Sentiment analysis module for Twitter financial news using Ray actors.

This module provides functionality to:
- Monitor Twitter filtered stream API for financial news accounts (async)
- Analyze sentiment of posts related to specific tickers (distributed via Ray)
- Calculate weighted sentiment scores based on engagement metrics
- Orchestrate distributed processing with Ray actors

Ray Actor Architecture:
- TwitterStreamMonitor: Async actor for streaming tweets
- SentimentAnalyzer: Parallel actors for sentiment analysis
- SentimentAggregator: Stateful actor for aggregating results
- SentimentOrchestrator: Coordinates all actors
"""

from .twitter_stream import TwitterStreamMonitor
from .sentiment_analyzer import SentimentAnalyzer
from .sentiment_aggregator import SentimentAggregator
from .ray_orchestrator import SentimentOrchestrator, run_sentiment_pipeline
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
    'SentimentOrchestrator',
    'run_sentiment_pipeline',
    'TweetData',
    'SentimentResult',
    'WeightedSentiment',
    'SentimentLabel',
    'TickerSentiment',
    'SentimentConfig',
    'utils',
]
