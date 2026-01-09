"""
Utility functions for sentiment analysis module with async support.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import ray

from .models import WeightedSentiment

logger = logging.getLogger(__name__)


def load_config_from_env() -> Dict[str, str]:
    """
    Load sentiment configuration from environment variables.
    
    Returns:
        Dictionary with configuration values from environment
    """
    return {
        'twitter_bearer_token': os.getenv('TWITTER_BEARER_TOKEN', ''),
        'sentiment_window_days': os.getenv('SENTIMENT_WINDOW_DAYS', '5'),
        'min_confidence_threshold': os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.6'),
        'use_gpu': os.getenv('USE_GPU', 'false'),
        'monitored_accounts': os.getenv(
            'MONITORED_ACCOUNTS',
            'Benzinga,fxhedgers,ZeroHedge,Finviz_com,FT'
        ),
        'target_tickers': os.getenv('TARGET_TICKERS', 'NVDA,MSFT,AAPL'),
        'sentiment_model': os.getenv(
            'SENTIMENT_MODEL',
            'cardiffnlp/twitter-roberta-base-sentiment'
        ),
    }


def export_sentiments_to_json(
    sentiments: Dict[str, WeightedSentiment],
    output_path: str
) -> None:
    """
    Export weighted sentiments to JSON file.
    
    Parameters:
        sentiments: Dictionary of ticker to WeightedSentiment
        output_path: Path to output JSON file
    """
    data = {
        'timestamp': datetime.now().isoformat(),
        'sentiments': {
            ticker: sentiment.to_dict()
            for ticker, sentiment in sentiments.items()
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Exported {len(sentiments)} sentiments to {output_path}")


def load_sentiments_from_json(input_path: str) -> Dict[str, Dict]:
    """
    Load weighted sentiments from JSON file.
    
    Parameters:
        input_path: Path to input JSON file
        
    Returns:
        Dictionary of loaded sentiment data
    """
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    logger.info(
        f"Loaded {len(data.get('sentiments', {}))} sentiments from {input_path}"
    )
    
    return data


def calculate_sentiment_change(
    current: WeightedSentiment,
    previous: WeightedSentiment
) -> float:
    """
    Calculate percentage change in sentiment score.
    
    Parameters:
        current: Current weighted sentiment
        previous: Previous weighted sentiment
        
    Returns:
        Percentage change in sentiment score
    """
    if previous.weighted_score == 0:
        return 0.0
    
    change = (
        (current.weighted_score - previous.weighted_score)
        / abs(previous.weighted_score)
        * 100
    )
    
    return change


def format_sentiment_report(
    sentiments: Dict[str, WeightedSentiment]
) -> str:
    """
    Format weighted sentiments as a readable report.
    
    Parameters:
        sentiments: Dictionary of ticker to WeightedSentiment
        
    Returns:
        Formatted report string
    """
    lines = ["=" * 60]
    lines.append("SENTIMENT ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Sort by weighted score (most bullish first)
    sorted_sentiments = sorted(
        sentiments.items(),
        key=lambda x: x[1].weighted_score,
        reverse=True
    )
    
    for ticker, sentiment in sorted_sentiments:
        lines.append(f"\n{ticker}")
        lines.append("-" * 30)
        lines.append(f"  Direction:        {sentiment.sentiment_direction}")
        lines.append(f"  Weighted Score:   {sentiment.weighted_score:+.4f}")
        lines.append(f"  Total Tweets:     {sentiment.total_tweets}")
        lines.append(f"  Avg Confidence:   {sentiment.average_confidence:.3f}")
        lines.append(
            f"  Positive Weight:  {sentiment.positive_weight:.2f}"
        )
        lines.append(
            f"  Negative Weight:  {sentiment.negative_weight:.2f}"
        )
        lines.append(
            f"  Neutral Weight:   {sentiment.neutral_weight:.2f}"
        )
        lines.append(
            f"  Window:           {sentiment.window_start.strftime('%Y-%m-%d')} "
            f"to {sentiment.window_end.strftime('%Y-%m-%d')}"
        )
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def get_sentiment_summary(
    sentiments: Dict[str, WeightedSentiment]
) -> Dict[str, int]:
    """
    Get summary statistics of sentiment directions.
    
    Parameters:
        sentiments: Dictionary of ticker to WeightedSentiment
        
    Returns:
        Dictionary with counts of bullish, bearish, and neutral sentiments
    """
    summary = {
        'bullish': 0,
        'bearish': 0,
        'neutral': 0
    }
    
    for sentiment in sentiments.values():
        direction = sentiment.sentiment_direction.lower()
        summary[direction] = summary.get(direction, 0) + 1
    
    return summary


def is_significant_sentiment(
    sentiment: WeightedSentiment,
    min_tweets: int = 5,
    min_confidence: float = 0.6
) -> bool:
    """
    Check if sentiment is statistically significant.
    
    Parameters:
        sentiment: Weighted sentiment to check
        min_tweets: Minimum number of tweets required
        min_confidence: Minimum average confidence required
        
    Returns:
        True if sentiment is significant, False otherwise
    """
    return (
        sentiment.total_tweets >= min_tweets
        and sentiment.average_confidence >= min_confidence
    )


def filter_significant_sentiments(
    sentiments: Dict[str, WeightedSentiment],
    min_tweets: int = 5,
    min_confidence: float = 0.6
) -> Dict[str, WeightedSentiment]:
    """
    Filter sentiments to only include significant ones.
    
    Parameters:
        sentiments: Dictionary of ticker to WeightedSentiment
        min_tweets: Minimum number of tweets required
        min_confidence: Minimum average confidence required
        
    Returns:
        Filtered dictionary of significant sentiments
    """
    return {
        ticker: sentiment
        for ticker, sentiment in sentiments.items()
        if is_significant_sentiment(sentiment, min_tweets, min_confidence)
    }


async def get_actor_sentiments(
    aggregator_actor: object,  # Ray actor handle
    ticker: Optional[str] = None
) -> Optional[WeightedSentiment] | Dict[str, WeightedSentiment]:
    """
    Get sentiment(s) from Ray aggregator actor asynchronously.
    
    Parameters:
        aggregator_actor: Ray actor handle for sentiment aggregator
        ticker: Optional ticker symbol (if None, returns all sentiments)
        
    Returns:
        WeightedSentiment for single ticker or dict of all sentiments
    """
    if ticker:
        result = aggregator_actor.get_weighted_sentiment_async.remote(ticker)  # type: ignore
        return await result
    else:
        result = aggregator_actor.get_all_weighted_sentiments_async.remote()  # type: ignore
        return await result


async def export_actor_sentiments_to_json(
    aggregator_actor: object,  # Ray actor handle
    output_path: str
) -> None:
    """
    Export sentiments from Ray actor to JSON file asynchronously.
    
    Parameters:
        aggregator_actor: Ray actor handle for sentiment aggregator
        output_path: Path to output JSON file
    """
    sentiments = await get_actor_sentiments(aggregator_actor)
    if isinstance(sentiments, dict):
        export_sentiments_to_json(sentiments, output_path)
    else:
        logger.warning("No sentiments to export")


def wait_for_actor_ready(actor: object, timeout: int = 30) -> bool:  # Ray actor handle
    """
    Wait for a Ray actor to be ready.
    
    Parameters:
        actor: Ray actor handle
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if actor is ready, False if timeout
    """
    try:
        ray.get(actor.is_running.remote(), timeout=timeout)  # type: ignore
        return True
    except Exception as e:
        logger.error(f"Actor not ready within {timeout}s: {e}")
        return False
