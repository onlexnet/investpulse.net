"""
Sentiment analysis for financial tweets using transformer models.
"""

import logging
from typing import Any, Dict, Optional
import torch  # type: ignore
from transformers import (  # type: ignore
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)

from .config import SentimentConfig
from .models import TweetData, SentimentResult, SentimentLabel

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyze sentiment of financial tweets using pre-trained transformer models.
    
    Uses cardiffnlp/twitter-roberta-base-sentiment model for sentiment
    classification with confidence scores.
    """
    
    def __init__(self, config: SentimentConfig):
        """
        Initialize sentiment analyzer with pre-trained model.
        
        Parameters:
            config: Sentiment analysis configuration
        """
        self.config = config
        self.model_name = config.sentiment_model
        self.device = "cuda" if config.use_gpu and torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing sentiment analyzer on device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )
        
        # Create sentiment analysis pipeline
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
            return_all_scores=True
        )
        
        # Label mapping for the model
        self.label_mapping = {
            "LABEL_0": SentimentLabel.NEGATIVE,
            "LABEL_1": SentimentLabel.NEUTRAL,
            "LABEL_2": SentimentLabel.POSITIVE
        }
        
        logger.info("Sentiment analyzer initialized successfully")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess tweet text for sentiment analysis.
        
        Cleans and normalizes text while preserving sentiment-relevant
        information like emphasis and financial context.
        
        Parameters:
            text: Raw tweet text
            
        Returns:
            Preprocessed text ready for analysis
        """
        # Remove URLs
        text = ' '.join(
            word for word in text.split() if not word.startswith('http')
        )
        
        # Remove mentions (but keep the context)
        text = text.replace('@', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_sentiment_from_scores(
        self,
        scores: list[Any]
    ) -> tuple[SentimentLabel, float, Dict[str, float]]:
        """
        Extract sentiment label and confidence from model output scores.
        
        Parameters:
            scores: List of score dictionaries from the model
            
        Returns:
            Tuple of (sentiment_label, confidence, score_dict)
        """
        # Convert list of scores to dictionary
        score_dict: Dict[str, float] = {}
        first_result = scores[0] if scores else []
        
        for item in first_result:
            if isinstance(item, dict):
                label_str = str(item.get('label', ''))
                score_val = float(item.get('score', 0.0))
                if label_str in self.label_mapping:
                    score_dict[self.label_mapping[label_str].value] = score_val
        
        # Find label with highest score
        max_label = max(
            first_result,
            key=lambda x: float(x.get('score', 0.0)) if isinstance(x, dict) else 0.0
        )
        
        if isinstance(max_label, dict):
            label_key = str(max_label.get('label', ''))
            sentiment = self.label_mapping.get(
                label_key,
                SentimentLabel.NEUTRAL
            )
            confidence = float(max_label.get('score', 0.0))
        else:
            sentiment = SentimentLabel.NEUTRAL
            confidence = 0.0
        
        return sentiment, confidence, score_dict
    
    def analyze(self, tweet_data: TweetData) -> Optional[SentimentResult]:
        """
        Analyze sentiment of a tweet.
        
        Parameters:
            tweet_data: Tweet data to analyze
            
        Returns:
            SentimentResult with sentiment classification and confidence,
            or None if analysis fails
        """
        try:
            # Preprocess tweet text
            text = self._preprocess_text(tweet_data.text)
            
            # Skip if text is too short
            if len(text.strip()) < 10:
                logger.debug(
                    f"Skipping tweet {tweet_data.tweet_id}: text too short"
                )
                return None
            
            # Run sentiment analysis
            logger.debug(f"Analyzing tweet {tweet_data.tweet_id}: {text[:50]}...")
            result = self.pipeline(text[:512])  # Truncate to model max length
            
            # Extract sentiment and confidence
            sentiment, confidence, scores = self._extract_sentiment_from_scores(
                result
            )
            
            # Create sentiment result
            sentiment_result = SentimentResult(
                tweet_data=tweet_data,
                sentiment=sentiment,
                confidence=confidence,
                scores=scores
            )
            
            logger.info(
                f"Tweet {tweet_data.tweet_id} sentiment: {sentiment.value} "
                f"(confidence: {confidence:.3f})"
            )
            
            return sentiment_result
            
        except Exception as e:
            logger.error(
                f"Error analyzing sentiment for tweet {tweet_data.tweet_id}: {e}"
            )
            return None
    
    def analyze_batch(
        self,
        tweets: list[TweetData]
    ) -> list[SentimentResult]:
        """
        Analyze sentiment for multiple tweets in batch.
        
        Batch processing can be more efficient for multiple tweets.
        
        Parameters:
            tweets: List of tweet data to analyze
            
        Returns:
            List of sentiment results (may be shorter if some analyses fail)
        """
        results = []
        
        for tweet_data in tweets:
            result = self.analyze(tweet_data)
            if result:
                results.append(result)
        
        logger.info(
            f"Batch analysis complete: {len(results)}/{len(tweets)} successful"
        )
        
        return results
    
    def is_high_confidence(self, result: SentimentResult) -> bool:
        """
        Check if sentiment result meets confidence threshold.
        
        Parameters:
            result: Sentiment result to check
            
        Returns:
            True if confidence exceeds minimum threshold
        """
        return result.confidence >= self.config.min_confidence_threshold
