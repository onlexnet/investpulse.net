"""
Configuration settings for sentiment analysis module.
"""

import os
from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class SentimentConfig:
    """
    Configuration for sentiment analysis module.
    
    Attributes:
        monitored_accounts: List of Twitter accounts to monitor
        target_tickers: Set of stock tickers to analyze
        sentiment_window_days: Number of days to consider for weighted sentiment
        twitter_bearer_token: Twitter API v2 Bearer Token for authentication
        min_confidence_threshold: Minimum confidence score to accept sentiment
    """
    
    monitored_accounts: List[str] = field(default_factory=lambda: [
        'Benzinga',
        'fxhedgers',
        'ZeroHedge',
        'Finviz_com',
        'FT'
    ])
    
    target_tickers: Set[str] = field(default_factory=lambda: {
        'NVDA',
        'MSFT',
        'AAPL'
    })
    
    sentiment_window_days: int = 5
    twitter_bearer_token: str = field(default_factory=lambda: os.getenv('TWITTER_BEARER_TOKEN', ''))
    min_confidence_threshold: float = 0.6
    
    # Twitter API configuration
    max_results_per_request: int = 100
    stream_timeout: int = 90  # seconds
    
    # Sentiment model configuration
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment"
    use_gpu: bool = False
    
    def add_ticker(self, ticker: str) -> None:
        """
        Add a ticker to the monitoring list.
        
        Parameters:
            ticker: Stock ticker symbol to add
        """
        self.target_tickers.add(ticker.upper())
    
    def remove_ticker(self, ticker: str) -> None:
        """
        Remove a ticker from the monitoring list.
        
        Parameters:
            ticker: Stock ticker symbol to remove
        """
        self.target_tickers.discard(ticker.upper())
    
    def add_account(self, account: str) -> None:
        """
        Add an account to the monitoring list.
        
        Parameters:
            account: Twitter account handle (without @)
        """
        account_clean = account.lstrip('@')
        if account_clean not in self.monitored_accounts:
            self.monitored_accounts.append(account_clean)
    
    def remove_account(self, account: str) -> None:
        """
        Remove an account from the monitoring list.
        
        Parameters:
            account: Twitter account handle (with or without @)
        """
        account_clean = account.lstrip('@')
        if account_clean in self.monitored_accounts:
            self.monitored_accounts.remove(account_clean)
