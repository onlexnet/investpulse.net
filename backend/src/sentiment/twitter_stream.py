"""
Twitter Filtered Stream API monitor for financial news accounts.
"""

import re
import logging
from datetime import datetime
from typing import Callable, List, Optional, Set
import tweepy  # type: ignore
from tweepy.streaming import StreamRule  # type: ignore

from .config import SentimentConfig
from .models import TweetData

logger = logging.getLogger(__name__)


class TwitterStreamMonitor:
    """
    Monitor Twitter filtered stream API for financial news accounts.
    
    This class connects to Twitter API v2 filtered stream and monitors
    tweets from specified financial news accounts, extracting relevant
    ticker symbols and engagement metrics.
    """
    
    def __init__(
        self,
        config: SentimentConfig,
        on_tweet_callback: Optional[Callable[[TweetData], None]] = None
    ):
        """
        Initialize Twitter stream monitor.
        
        Parameters:
            config: Sentiment analysis configuration
            on_tweet_callback: Callback function to process incoming tweets
        """
        self.config = config
        self.on_tweet_callback = on_tweet_callback
        self.client: Optional[tweepy.StreamingClient] = None
        self._ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b|\b([A-Z]{2,5})\b')
        
    def _create_client(self) -> tweepy.StreamingClient:
        """
        Create and configure Twitter streaming client.
        
        Returns:
            Configured StreamingClient instance
            
        Raises:
            ValueError: If bearer token is not configured
        """
        if not self.config.twitter_bearer_token:
            raise ValueError(
                "Twitter bearer token not configured. "
                "Set config.twitter_bearer_token"
            )
        
        client = tweepy.StreamingClient(
            bearer_token=self.config.twitter_bearer_token,
            wait_on_rate_limit=True
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
    
    def _parse_tweet(self, tweet: tweepy.Tweet) -> Optional[TweetData]:
        """
        Parse raw tweet data into TweetData model.
        
        Parameters:
            tweet: Raw tweet object from Tweepy
            
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
            
            # Get author username
            author_username = "unknown"
            if hasattr(tweet, 'author') and tweet.author:
                author_username = tweet.author.username
            elif hasattr(tweet, 'includes') and 'users' in tweet.includes:
                # Try to find author in includes
                for user in tweet.includes['users']:
                    if user.id == tweet.author_id:
                        author_username = user.username
                        break
            
            tweet_data = TweetData(
                tweet_id=tweet.id,
                text=tweet.text,
                author_username=author_username,
                created_at=tweet.created_at or datetime.now(),
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
    
    def _setup_stream_rules(self) -> None:
        """
        Configure filtered stream rules for monitored accounts.
        
        Creates rules to filter tweets from specified financial news accounts.
        Deletes existing rules before adding new ones.
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call start() first.")
        
        # Delete existing rules
        existing_rules = self.client.get_rules()
        if existing_rules and existing_rules.data:
            rule_ids = [rule.id for rule in existing_rules.data]
            self.client.delete_rules(rule_ids)
            logger.info(f"Deleted {len(rule_ids)} existing stream rules")
        
        # Create new rules for monitored accounts
        rules = []
        for account in self.config.monitored_accounts:
            rule = StreamRule(
                value=f"from:{account}",
                tag=f"monitor_{account}"
            )
            rules.append(rule)
        
        # Add rules in batch
        if rules:
            self.client.add_rules(rules)
            logger.info(
                f"Added {len(rules)} stream rules for accounts: "
                f"{', '.join(self.config.monitored_accounts)}"
            )
    
    def start(self) -> None:
        """
        Start monitoring Twitter filtered stream.
        
        Sets up stream rules and begins listening for tweets from
        configured accounts. Calls the callback function for each
        relevant tweet containing target tickers.
        
        This is a blocking call that runs until interrupted.
        """
        logger.info("Starting Twitter stream monitor")
        
        # Initialize client
        self.client = self._create_client()
        
        # Setup filtering rules
        self._setup_stream_rules()
        
        # Start filtering stream with expansions and fields
        logger.info("Connecting to filtered stream...")
        
        try:
            aaa = self.client.filter(
                expansions=['author_id'])
            for rule in aaa:
                pass
            # Stream tweets with enhanced data
            for tweet in self.client.filter(
                expansions=['author_id'],
                tweet_fields=[
                    'created_at',
                    'public_metrics',
                    'referenced_tweets'
                ],
                user_fields=['username']
            ):
                # Parse tweet data
                tweet_data = self._parse_tweet(tweet)
                
                # Process tweet if it contains target tickers
                if tweet_data and self.on_tweet_callback:
                    self.on_tweet_callback(tweet_data)
                    
        except KeyboardInterrupt:
            logger.info("Stream monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in stream monitoring: {e}")
            raise
    
    def stop(self) -> None:
        """
        Stop monitoring Twitter stream.
        
        Disconnects from the streaming API and cleans up resources.
        """
        if self.client:
            self.client.disconnect()
            logger.info("Twitter stream monitor stopped")
