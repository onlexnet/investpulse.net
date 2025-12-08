"""
Ray orchestrator for coordinating sentiment analysis actors.

This module provides the main orchestrator that coordinates Twitter streaming,
sentiment analysis, and aggregation using Ray actors.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
import ray

from .config import SentimentConfig
from .twitter_stream import TwitterStreamMonitor
from .sentiment_analyzer import SentimentAnalyzer
from .sentiment_aggregator import SentimentAggregator
from .models import WeightedSentiment

logger = logging.getLogger(__name__)


@ray.remote
class SentimentOrchestrator:
    """
    Ray actor for orchestrating distributed sentiment analysis.
    
    This actor coordinates:
    - Twitter stream monitoring (TwitterStreamMonitor actor)
    - Sentiment analysis (SentimentAnalyzer actors - can scale)
    - Sentiment aggregation (SentimentAggregator actor - single instance)
    
    Benefits of being an actor:
    - Remote access from any Ray worker
    - State management by Ray
    - Fault tolerance and supervision
    - Consistent actor-based architecture
    """
    
    def __init__(
        self,
        config: SentimentConfig,
        num_analyzers: int = 2
    ):
        """
        Initialize sentiment orchestrator as Ray actor.
        
        Parameters:
            config: Sentiment analysis configuration
            num_analyzers: Number of parallel sentiment analyzer actors
        """
        self.config = config
        self.num_analyzers = num_analyzers
        
        # Actor handles
        self.aggregator_actor: Any = None
        self.analyzer_actors: list[Any] = []
        self.stream_actor: Any = None
        
        self._running = False
        self._initialized = False
        
        logger.info(
            f"Initialized sentiment orchestrator actor with {num_analyzers} analyzers"
        )
    
    async def initialize(self) -> bool:
        """
        Initialize all child actors.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            logger.warning("Orchestrator already initialized")
            return True
        
        logger.info("Initializing child actors...")
        
        try:
            # Create aggregator actor (single instance, stateful)
            self.aggregator_actor = SentimentAggregator.remote(self.config)
            logger.info("Created aggregator actor")
            
            # Create analyzer actors (multiple instances for parallel processing)
            for i in range(self.num_analyzers):
                analyzer = SentimentAnalyzer.remote(
                    self.config,
                    self.aggregator_actor
                )
                self.analyzer_actors.append(analyzer)
                logger.info(f"Created analyzer actor {i+1}/{self.num_analyzers}")
            
            # Create stream monitor actor
            self.stream_actor = TwitterStreamMonitor.remote(
                self.config,
                self.analyzer_actors[0]  # Start with first analyzer
            )
            logger.info("Created stream monitor actor")
            
            self._initialized = True
            logger.info("All child actors initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize actors: {e}")
            return False
    
    async def start(self) -> bool:
        """
        Start the sentiment analysis pipeline.
        
        Starts the Twitter stream monitor which will feed tweets to analyzers,
        which in turn update the aggregator.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self._initialized:
            logger.error("Cannot start: actors not initialized. Call initialize() first.")
            return False
        
        if self._running:
            logger.warning("Pipeline already running")
            return True
        
        logger.info("Starting sentiment analysis pipeline...")
        
        try:
            # Start the stream monitor (async, non-blocking)
            self.stream_actor.start.remote()  # type: ignore
            self._running = True
            logger.info("Sentiment analysis pipeline started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop the sentiment analysis pipeline.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self._running:
            logger.warning("Pipeline not running")
            return True
        
        logger.info("Stopping sentiment analysis pipeline...")
        
        try:
            if self.stream_actor:
                ray.get(self.stream_actor.stop.remote())  # type: ignore
            
            self._running = False
            logger.info("Sentiment analysis pipeline stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop pipeline: {e}")
            return False
    
    async def get_sentiments(
        self,
        ticker: Optional[str] = None
    ) -> Optional[WeightedSentiment | Dict[str, WeightedSentiment]]:
        """
        Get sentiment data from the aggregator asynchronously.
        
        Parameters:
            ticker: Optional ticker symbol (if None, returns all sentiments)
            
        Returns:
            WeightedSentiment for single ticker or dict of all sentiments, None if error
        """
        if not self.aggregator_actor:
            logger.error("Cannot get sentiments: actors not initialized")
            return None
        
        try:
            if ticker:
                result = self.aggregator_actor.get_weighted_sentiment_async.remote(  # type: ignore
                    ticker
                )
            else:
                result = self.aggregator_actor.get_all_weighted_sentiments_async.remote()  # type: ignore
            
            return await result
            
        except Exception as e:
            logger.error(f"Failed to get sentiments: {e}")
            return None
    
    def get_sentiments_sync(
        self,
        ticker: Optional[str] = None
    ) -> Optional[WeightedSentiment | Dict[str, WeightedSentiment]]:
        """
        Get sentiment data synchronously (blocking).
        
        Parameters:
            ticker: Optional ticker symbol (if None, returns all sentiments)
            
        Returns:
            WeightedSentiment for single ticker or dict of all sentiments, None if error
        """
        if not self.aggregator_actor:
            logger.error("Cannot get sentiments: actors not initialized")
            return None
        
        try:
            if ticker:
                result = self.aggregator_actor.get_weighted_sentiment.remote(ticker)  # type: ignore
            else:
                result = self.aggregator_actor.get_all_weighted_sentiments.remote()  # type: ignore
            
            return ray.get(result)
            
        except Exception as e:
            logger.error(f"Failed to get sentiments: {e}")
            return None
    
    async def cleanup(self) -> None:
        """
        Clean up resources and shutdown child actors.
        
        This method should be called before the orchestrator actor is killed.
        """
        logger.info("Cleaning up sentiment orchestrator...")
        
        # Stop pipeline first
        await self.stop()
        
        # Kill all child actors
        try:
            if self.stream_actor:
                ray.kill(self.stream_actor)
                logger.info("Killed stream actor")
            
            for i, analyzer in enumerate(self.analyzer_actors):
                ray.kill(analyzer)
                logger.debug(f"Killed analyzer actor {i+1}")
            
            if self.aggregator_actor:
                ray.kill(self.aggregator_actor)
                logger.info("Killed aggregator actor")
            
            self._initialized = False
            logger.info("Sentiment orchestrator cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def is_running(self) -> bool:
        """
        Check if the orchestrator is currently running.
        
        Returns:
            True if running, False otherwise
        """
        return self._running
    
    def is_initialized(self) -> bool:
        """
        Check if the orchestrator has been initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self._initialized
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the orchestrator and its actors.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            "initialized": self._initialized,
            "running": self._running,
            "num_analyzers": self.num_analyzers,
            "has_aggregator": self.aggregator_actor is not None,
            "has_stream": self.stream_actor is not None,
            "analyzer_count": len(self.analyzer_actors)
        }
        
        # Check if stream is running
        if self.stream_actor and self._initialized:
            try:
                stream_running = ray.get(self.stream_actor.is_running.remote())  # type: ignore
                status["stream_running"] = stream_running
            except Exception as e:
                logger.error(f"Failed to check stream status: {e}")
                status["stream_running"] = None
        
        return status


async def run_sentiment_pipeline(
    config: SentimentConfig,
    duration_seconds: Optional[int] = None,
    num_analyzers: int = 2
) -> Dict[str, WeightedSentiment]:
    """
    Run the complete sentiment analysis pipeline using orchestrator actor.
    
    Parameters:
        config: Sentiment analysis configuration
        duration_seconds: How long to run (None = run indefinitely)
        num_analyzers: Number of parallel sentiment analyzer actors
        
    Returns:
        Dictionary of final weighted sentiments by ticker
    """
    # Initialize Ray if not already done
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
        logger.info("Ray initialized")
    
    # Create orchestrator actor
    orchestrator = SentimentOrchestrator.remote(config, num_analyzers)
    
    try:
        # Initialize and start
        init_success = await orchestrator.initialize.remote()
        if not init_success:
            logger.error("Failed to initialize orchestrator")
            return {}
        
        start_success = await orchestrator.start.remote()
        if not start_success:
            logger.error("Failed to start pipeline")
            return {}
        
        # Run for specified duration or indefinitely
        if duration_seconds:
            logger.info(f"Running pipeline for {duration_seconds} seconds...")
            await asyncio.sleep(duration_seconds)
        else:
            logger.info("Running pipeline indefinitely (Ctrl+C to stop)...")
            while True:
                await asyncio.sleep(60)
                # Optionally print status every minute
                status = await orchestrator.get_status.remote()
                logger.info(f"Status: {status}")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    finally:
        # Get final sentiments
        final_sentiments = await orchestrator.get_sentiments.remote()
        
        # Cleanup
        await orchestrator.cleanup.remote()
        ray.kill(orchestrator)
        
        if isinstance(final_sentiments, dict):
            return final_sentiments
        else:
            return {}
