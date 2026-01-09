"""
Twitter API v2 polling monitor for financial news accounts using async Ray actors.
"""

import re
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Callable, List, Optional, Set, Dict
import tweepy  # type: ignore
import ray

from .config import SentimentConfig
from .models import TweetData

logger = logging.getLogger(__name__)


@ray.remote
class TwitterStreamMonitor:
    """
    Ray actor for monitoring Twitter API v2 for financial news accounts using polling.
    
    This async actor polls Twitter API v2 for tweets from specified financial news
    accounts, extracting relevant ticker symbols and engagement metrics.
    """
    
    def __init__(
        self,
        config: SentimentConfig,
        analyzer_actor: Optional[object] = None  # Ray actor handle
    ):
        """
        Initialize Twitter polling monitor as Ray actor.
        
        Parameters:
            config: Sentiment analysis configuration
            analyzer_actor: Ray actor handle for sentiment analyzer
        """
        self.config = config
        self.analyzer_actor = analyzer_actor
        self.client: Optional[tweepy.Client] = None
        self._ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b|\b([A-Z]{2,5})\b')
        self._running = False
        self._last_tweet_ids: Dict[str, str] = {}  # Track last seen tweet per account
        self._poll_interval = 60  # Poll every 60 seconds
        
    def _create_client(self) -> tweepy.Client:
        """
        Create and configure Twitter API v2 client for polling.
        
        Returns:
            Configured Client instance
            
        Raises:
            ValueError: If bearer token is not configured
        """
        if not self.config.twitter_bearer_token:
            raise ValueError(
                "Twitter bearer token not configured. "
                "Set config.twitter_bearer_token"
            )
        
        client = tweepy.Client(
            bearer_token=self.config.twitter_bearer_token,
            wait_on_rate_limit=True,
        )
        
        return client
    
    def _extract_tickers(self, text: str) -> List[str]:
        """
        Extract stock ticker symbols from tweet text.
        
        Looks for:
        - Cashtags ($AAPL, $MSFT)
        - Uppercase ticker symbols in context
        
        Parameters:
            text: Tweet text to analyze
            
        Returns:
            List of unique ticker symbols found in the text
        """
        tickers: Set[str] = set()
        
        # Find all potential tickers
        for match in self._ticker_pattern.finditer(text):
            ticker = match.group(1) or match.group(2)
            if ticker and ticker in self.config.target_tickers:
                tickers.add(ticker)
        
        return list(tickers)
    
    def _parse_tweet(self, tweet: tweepy.Tweet, author_username: str) -> Optional[TweetData]:
        """
        Parse raw tweet data into TweetData model.
        
        Parameters:
            tweet: Raw tweet object from Tweepy
            author_username: Username of the tweet author
            
        Returns:
            TweetData object if tweet contains target tickers, None otherwise
        """
        try:
            # Extract tickers from tweet text
            tickers = self._extract_tickers(tweet.text)
            
            # Skip tweets without target tickers
            if not tickers:
                return None
            
            # Parse public metrics
            metrics = tweet.public_metrics or {}
            retweet_count = metrics.get('retweet_count', 0)
            like_count = metrics.get('like_count', 0)
            
            tweet_data = TweetData(
                tweet_id=str(tweet.id),
                text=tweet.text,
                author_username=author_username,
                created_at=tweet.created_at or datetime.now(timezone.utc),
                retweet_count=retweet_count,
                like_count=like_count,
                mentioned_tickers=tickers
            )
            
            logger.info(
                f"Parsed tweet {tweet_data.tweet_id} from "
                f"@{author_username} mentioning {tickers}"
            )
            
            return tweet_data
            
        except Exception as e:
            logger.error(f"Error parsing tweet {tweet.id}: {e}")
            return None
    
    async def _fetch_user_tweets(self, username: str) -> List[tweepy.Tweet]:
        """
        Fetch recent tweets from a specific user.
        
        Parameters:
            username: Twitter username to fetch tweets from
            
        Returns:
            List of tweet objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call start() first.")
        
        try:
            # Get user ID from username
            user = self.client.get_user(username=username)
            if not user or not user.data:
                logger.warning(f"User not found: {username}")
                return []
            
            user_id = user.data.id
            
            # Fetch recent tweets
            kwargs = {
                'id': user_id,
                'max_results': min(self.config.max_results_per_request, 100),
                'tweet_fields': ['created_at', 'public_metrics', 'referenced_tweets'],
                'exclude': ['retweets', 'replies']  # Only original tweets
            }
            
            # Add since_id if we have a last seen tweet for this user
            if username in self._last_tweet_ids:
                kwargs['since_id'] = self._last_tweet_ids[username]
            else:
                # First time polling - only get tweets from last hour
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
                kwargs['start_time'] = start_time
            
            response = self.client.get_users_tweets(**kwargs)
            
            if response and response.data:
                # Update last seen tweet ID
                self._last_tweet_ids[username] = str(response.data[0].id)
                return list(response.data)
            
            return []
            
        except tweepy.TweepyException as e:
            logger.error(f"Error fetching tweets for {username}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching tweets for {username}: {e}")
            return []
    
    async def start(self) -> None:
        """
        Start monitoring Twitter API by polling asynchronously.
        
        Polls Twitter API for tweets from configured accounts at regular intervals.
        Sends tweets to analyzer actor for processing.
        
        This is an async method that runs until stopped.
        """
        logger.info("Starting Twitter polling monitor (async)")
        self._running = True
        
        # Initialize client
        self.client = self._create_client()
        
        logger.info(
            f"Starting to poll {len(self.config.monitored_accounts)} accounts "
            f"every {self._poll_interval} seconds"
        )
        
        try:
            while self._running:
                # Poll all monitored accounts
                await self._poll_accounts()
                
                # Wait before next poll
                await asyncio.sleep(self._poll_interval)
                    
        except asyncio.CancelledError:
            logger.info("Polling monitoring cancelled")
            self._running = False
        except Exception as e:
            logger.error(f"Error in polling monitoring: {e}")
            self._running = False
            raise
    
    async def _poll_accounts(self) -> None:
        """
        Poll all monitored accounts for new tweets.
        """
        for account in self.config.monitored_accounts:
            if not self._running:
                break
                
            try:
                # Fetch tweets from this account
                tweets = await self._fetch_user_tweets(account)
                
                if tweets:
                    logger.info(f"Found {len(tweets)} new tweets from @{account}")
                    
                    # Process each tweet
                    for tweet in tweets:
                        # Parse tweet data
                        tweet_data = self._parse_tweet(tweet, account)
                        
                        # Send to analyzer actor if available
                        if tweet_data and self.analyzer_actor:
                            # Fire and forget - don't wait for result
                            self.analyzer_actor.analyze_tweet.remote(tweet_data)  # type: ignore
                            
            except Exception as e:
                logger.error(f"Error polling account @{account}: {e}")
    
    def stop(self) -> None:
        """
        Stop monitoring Twitter API polling.
        
        Cleans up resources and stops the polling loop.
        """
        self._running = False
        logger.info("Twitter polling monitor stopped")
    
    def is_running(self) -> bool:
        """
        Check if the polling monitor is currently running.
        
        Returns:
            True if running, False otherwise
        """
        return self._running
    
    def set_poll_interval(self, seconds: int) -> None:
        """
        Set the polling interval.
        
        Parameters:
            seconds: Number of seconds between polls (minimum 15)
        """
        if seconds < 15:
            logger.warning("Poll interval must be at least 15 seconds, setting to 15")
            seconds = 15
        self._poll_interval = seconds
        logger.info(f"Poll interval set to {seconds} seconds")
