package net.investpulse.sentiment.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.ScoredRedditPost;
import net.investpulse.common.dto.SentimentResult;
import net.investpulse.sentiment.converter.RedditPostConverter;
import net.investpulse.sentiment.persistence.ParquetSentimentWriter;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.concurrent.ExecutionException;

/**
 * Consumes raw tweets and Reddit posts, performs sentiment analysis,
 * and publishes results to both Kafka and Parquet files.
 * 
 * <p><strong>Data Sources:</strong>
 * <ul>
 *   <li>{@code ticker-*} topics: Raw tweets from X API via TwitterIngestor</li>
 *   <li>{@code reddit-scored-*} topics: Scored Reddit posts from RedditIngestor</li>
 * </ul>
 * 
 * <p><strong>Dual-Write Architecture:</strong>
 * <ul>
 *   <li>Synchronously publishes {@link SentimentResult} to {@code sentiment-aggregated} topic</li>
 *   <li>Asynchronously persists to Parquet files for Spark analytics</li>
 *   <li>Kafka offsets are committed <strong>only after</strong> Parquet write confirms success</li>
 * </ul>
 * 
 * <p><strong>Commit Strategy:</strong>
 * Manual acknowledgment mode ensures at-least-once delivery guarantee for file persistence.
 * If Parquet write fails, the offset is NOT committed, and the message will be reprocessed
 * after consumer rebalancing.
 * 
 * <p><strong>Timestamp Handling:</strong>
 * All messages preserve their original timestamps (UTC) from the source:
 * <ul>
 *   <li>Twitter: {@code createdAt} from X API</li>
 *   <li>Reddit: {@code timestamp} from ScoredRedditPost</li>
 * </ul>
 * Original timestamps are used for Parquet partition date calculation (converted to local timezone).
 * 
 * <p><strong>TODO:</strong> Add timeout mechanism for Parquet write confirmation to prevent
 * indefinite blocking. Consider circuit breaker pattern if write latency exceeds threshold.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SentimentAggregator {

    private static final String TOPIC_PREFIX = "ticker-";
    private static final String REDDIT_TOPIC_PREFIX = "reddit-scored-";
    private static final String OUTPUT_TOPIC = "sentiment-aggregated";
    private static final String EMPTY_STRING = "";

    private final FinancialSentimentService sentimentService;
    private final KafkaTemplate<String, SentimentResult> kafkaTemplate;
    private final ParquetSentimentWriter parquetWriter;
    private final RedditPostConverter redditConverter;

    /**
     * Processes tweets from dynamic {@code ticker-*} topics with manual offset management.
     * 
     * <p><strong>Processing Flow:</strong>
     * <ol>
     *   <li>Extract ticker symbol from topic name</li>
     *   <li>Perform sentiment analysis on tweet text</li>
     *   <li>Create {@link SentimentResult} record</li>
     *   <li>Publish to Kafka {@code sentiment-aggregated} topic (synchronous)</li>
     *   <li>Queue for async Parquet persistence</li>
     *   <li>Await Parquet write confirmation</li>
     *   <li>Acknowledge Kafka offset (commit)</li>
     * </ol>
     * 
     * <p><strong>Error Handling:</strong>
     * Exceptions during Parquet write prevent offset acknowledgment, triggering redelivery.
     * 
     * <p><strong>TODO:</strong> Implement timeout for Parquet write await (e.g., 30 seconds)
     * to prevent consumer thread starvation if write operations stall. Consider fallback
     * strategy: log error, skip persistence, and acknowledge offset to maintain throughput.
     * 
     * @param tweet the raw tweet data from X API
     * @param topic the source Kafka topic (format: {@code ticker-SYMBOL})
     * @param acknowledgment manual acknowledgment handle for offset commit
     */
    @KafkaListener(topicPattern = "ticker-.*", groupId = "sentiment-analyzer-group")
    public void processTweet(@Payload RawTweet tweet, 
                             @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                             Acknowledgment acknowledgment) {
        
        var ticker = topic.replace(TOPIC_PREFIX, EMPTY_STRING);
        log.info("Processing tweet {} for ticker {}", tweet.id(), ticker);

        var score = sentimentService.analyze(tweet.text());
        var label = sentimentService.getSentimentLabel(score);

        var result = new SentimentResult(
            tweet.id(),
            ticker,
            score,
            label,
            Instant.now(),
            tweet.publisher(),
            tweet.source(),
            tweet.createdAt()  // Original timestamp from Twitter (UTC)
        );

        persistSentimentResult(result, tweet.id(), ticker, acknowledgment);
    }

    /**
     * Processes scored Reddit posts from dynamic {@code reddit-scored-*} topics.
     * 
     * <p><strong>Processing Flow:</strong>
     * <ol>
     *   <li>Convert ScoredRedditPost to normalized RawTweet format</li>
     *   <li>Extract ticker symbol from topic name</li>
     *   <li>Perform sentiment analysis on post text (if available)</li>
     *   <li>Create {@link SentimentResult} record with source="reddit"</li>
     *   <li>Publish to Kafka {@code sentiment-aggregated} topic (synchronous)</li>
     *   <li>Queue for async Parquet persistence</li>
     *   <li>Await Parquet write confirmation</li>
     *   <li>Acknowledge Kafka offset (commit)</li>
     * </ol>
     * 
     * <p><strong>Note:</strong> Reddit posts already have sentiment scores calculated by
     * RedditIngestor, but we perform sentiment analysis again for consistency with Twitter
     * processing pipeline and to ensure uniform scoring methodology.
     * 
     * @param redditPost the scored Reddit post from reddit-scored-* topic
     * @param topic the source Kafka topic (format: {@code reddit-scored-SYMBOL})
     * @param acknowledgment manual acknowledgment handle for offset commit
     */
    @KafkaListener(topicPattern = "reddit-scored-.*", groupId = "sentiment-analyzer-group")
    public void processRedditPost(@Payload ScoredRedditPost redditPost,
                                  @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                                  Acknowledgment acknowledgment) {
        
        var ticker = topic.replace(REDDIT_TOPIC_PREFIX, EMPTY_STRING);
        log.info("Processing Reddit post {} from r/{} for ticker {}", 
            redditPost.id(), redditPost.subreddit(), ticker);

        // Convert Reddit post to normalized RawTweet format
        var normalizedTweet = redditConverter.convert(redditPost);

        // Use Reddit's pre-calculated sentiment score (already analyzed by RedditIngestor)
        var score = redditPost.sentimentScore();  // -1.0 to +1.0
        var label = sentimentService.getSentimentLabel(score);

        var result = new SentimentResult(
            redditPost.id(),
            ticker,
            score,
            label,
            Instant.now(),
            normalizedTweet.publisher(),
            "reddit",
            redditPost.timestamp()  // Original timestamp from Reddit (UTC)
        );

        persistSentimentResult(result, redditPost.id(), ticker, acknowledgment);
    }

    /**
     * Common persistence logic for sentiment results from all sources.
     * 
     * <p>Handles:
     * <ul>
     *   <li>Publishing to Kafka sentiment-aggregated topic (synchronous)</li>
     *   <li>Queuing for async Parquet write</li>
     *   <li>Awaiting Parquet confirmation before committing offset</li>
     *   <li>Error handling and retry logic</li>
     * </ul>
     * 
     * @param result the sentiment analysis result
     * @param sourceId tweet or post ID for logging
     * @param ticker symbol for partitioning
     * @param acknowledgment manual acknowledgment handle
     */
    private void persistSentimentResult(SentimentResult result, 
                                       String sourceId, 
                                       String ticker,
                                       Acknowledgment acknowledgment) {
        // Dual write: Kafka (sync) + Parquet (async)
        var _ = kafkaTemplate.send(OUTPUT_TOPIC, ticker, result);
        log.info("Published sentiment result for ticker {}: {}", ticker, result.sentiment());
        
        // Await Parquet write confirmation before committing offset
        // This ensures at-least-once delivery guarantee for file persistence
        try {
            parquetWriter.writeAsync(result).get(); // Blocking wait for async completion
            
            // Only commit offset after successful Parquet persistence
            acknowledgment.acknowledge();
            log.debug("Committed offset for {} after successful Parquet write", sourceId);
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Interrupted while waiting for Parquet write for {}: {}",
                sourceId, e.getMessage());
            // Do NOT acknowledge - message will be redelivered
            
        } catch (ExecutionException e) {
            log.error("Parquet write failed for {} (ticker {}), offset NOT committed: {}",
                sourceId, ticker, e.getCause().getMessage(), e.getCause());
            // Do NOT acknowledge - message will be redelivered after rebalancing
        }
    }
}
