package net.investpulse.sentiment.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.SentimentResult;
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
 * Consumes raw tweets from {@code ticker-*} topics, performs sentiment analysis,
 * and publishes results to both Kafka and Parquet files.
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
 * <p><strong>TODO:</strong> Add timeout mechanism for Parquet write confirmation to prevent
 * indefinite blocking. Consider circuit breaker pattern if write latency exceeds threshold.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SentimentAggregator {

    private static final String TOPIC_PREFIX = "ticker-";
    private static final String OUTPUT_TOPIC = "sentiment-aggregated";
    private static final String EMPTY_STRING = "";

    private final FinancialSentimentService sentimentService;
    private final KafkaTemplate<String, SentimentResult> kafkaTemplate;
    private final ParquetSentimentWriter parquetWriter;

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
            tweet.source()
        );

        // Dual write: Kafka (sync) + Parquet (async)
        kafkaTemplate.send(OUTPUT_TOPIC, ticker, result);
        log.info("Published sentiment result for ticker {}: {}", ticker, label);
        
        // Await Parquet write confirmation before committing offset
        // This ensures at-least-once delivery guarantee for file persistence
        try {
            parquetWriter.writeAsync(result).get(); // Blocking wait for async completion
            
            // Only commit offset after successful Parquet persistence
            acknowledgment.acknowledge();
            log.debug("Committed offset for tweet {} after successful Parquet write", tweet.id());
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Interrupted while waiting for Parquet write for tweet {}: {}",
                tweet.id(), e.getMessage());
            // Do NOT acknowledge - message will be redelivered
            
        } catch (ExecutionException e) {
            log.error("Parquet write failed for tweet {} (ticker {}), offset NOT committed: {}",
                tweet.id(), ticker, e.getCause().getMessage(), e.getCause());
            // Do NOT acknowledge - message will be redelivered after rebalancing
        }
    }
}
