package net.investpulse.sentiment.persistence;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;

import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.apache.parquet.schema.MessageType;
import org.apache.parquet.schema.PrimitiveType;
import org.apache.parquet.schema.Types;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.SentimentResult;
import net.investpulse.sentiment.converter.RedditPostConverter;

/**
 * Async Parquet writer for {@link SentimentResult} records with Spark-optimized partitioning.
 * 
 * <p><strong>Architecture:</strong>
 * <ul>
 *   <li>Uses Parquet with direct file I/O - minimal Hadoop dependencies (no security framework)</li>
 *   <li>Custom {@link LocalOutputFile} bypasses Hadoop security APIs completely</li>
 *   <li>Bounded queue (capacity from config) buffers records for async writing</li>
 *   <li>When queue is full, records are <strong>dropped and logged</strong> to prevent blocking</li>
 *   <li>Files are rotated based on record count (default 1000) or time (default 5 min)</li>
 *   <li>Partition structure: {@code ticker=SYMBOL/year=YYYY/month=MM/day=DD/}</li>
 *   <li>Date partitioning uses local timezone (configurable via {@code sentiment.timezone})</li>
 *   <li>Original source timestamps (Twitter/Reddit) are preserved for analytics</li>
 *   <li>Snappy compression and optimized row group size (8MB) for streaming workloads</li>
 * </ul>
 * 
 * <p><strong>Timezone Handling:</strong>
 * <ul>
 *   <li>Partition dates are calculated from {@code originalTimestamp} in local timezone</li>
 *   <li>Example: Post created 2026-01-07 23:00 UTC in UTC+5:00 timezone → partition day=08</li>
 *   <li>Enables day-based partitioning aligned with business day, not UTC date</li>
 * </ul>
 * 
 * <p><strong>Kafka Integration:</strong>
 * Offsets should only be committed AFTER this writer confirms successful writes.
 * See {@link net.investpulse.sentiment.service.SentimentAggregator} for coordination.
 * 
 * <p><strong>Graceful Shutdown:</strong>
 * {@link #shutdown()} drains pending records and closes all open writers before JVM exits.
 */
@Slf4j
@Service
public class ParquetSentimentWriter {

    private static final int ROW_GROUP_SIZE = 8 * 1024 * 1024; // 8MB for faster flushes in streaming
    private static final int PAGE_SIZE = 1 * 1024 * 1024; // 1MB pages
    private static final Duration MAX_FILE_DURATION = Duration.ofMinutes(5);
    
    @Value("${sentiment.parquet.base-path:/data/sentiment}")
    private String basePath;
    
    @Value("${sentiment.parquet.max-records-per-file:1000}")
    private int maxRecordsPerFile;
    
    @Value("${sentiment.parquet.queue-capacity:10000}")
    private int queueCapacity;
    
    private final RedditPostConverter redditConverter;
    private LinkedBlockingQueue<WriteRequest> writeQueue;
    private final Map<String, WriterState> activeWriters = new ConcurrentHashMap<>();
    private final MessageType schema;

    public ParquetSentimentWriter(RedditPostConverter redditConverter) {
        this.redditConverter = redditConverter;
        this.schema = createSchema();
    }

    /**
     * Creates Parquet schema for {@link SentimentResult} records.
     */
    private MessageType createSchema() {
        return Types.buildMessage()
            .required(PrimitiveType.PrimitiveTypeName.BINARY).as(org.apache.parquet.schema.LogicalTypeAnnotation.stringType()).named("tweetId")
            .required(PrimitiveType.PrimitiveTypeName.BINARY).as(org.apache.parquet.schema.LogicalTypeAnnotation.stringType()).named("ticker")
            .required(PrimitiveType.PrimitiveTypeName.DOUBLE).named("score")
            .required(PrimitiveType.PrimitiveTypeName.BINARY).as(org.apache.parquet.schema.LogicalTypeAnnotation.stringType()).named("sentiment")
            .required(PrimitiveType.PrimitiveTypeName.INT64).as(org.apache.parquet.schema.LogicalTypeAnnotation.timestampType(true, org.apache.parquet.schema.LogicalTypeAnnotation.TimeUnit.MILLIS)).named("processedAt")
            .required(PrimitiveType.PrimitiveTypeName.BINARY).as(org.apache.parquet.schema.LogicalTypeAnnotation.stringType()).named("publisher")
            .required(PrimitiveType.PrimitiveTypeName.BINARY).as(org.apache.parquet.schema.LogicalTypeAnnotation.stringType()).named("source")
            .required(PrimitiveType.PrimitiveTypeName.INT64).as(org.apache.parquet.schema.LogicalTypeAnnotation.timestampType(true, org.apache.parquet.schema.LogicalTypeAnnotation.TimeUnit.MILLIS)).named("originalTimestamp")
            .named("SentimentResult");
    }

    /**
     * Initializes the write queue with configured capacity after dependency injection.
     */
    @PostConstruct
    public void init() {
        this.writeQueue = new LinkedBlockingQueue<>(queueCapacity);
        log.info("Initialized ParquetSentimentWriter (minimal Hadoop dependencies) with queue capacity: {}, base path: {}",
            queueCapacity, basePath);
    }

    /**
     * Asynchronously queues a {@link SentimentResult} for Parquet persistence.
     * 
     * <p><strong>Drop-and-Log Policy:</strong>
     * If the write queue is full (capacity: {@code queue-capacity}), the record is
     * <strong>dropped</strong> and a warning is logged. This prevents blocking the
     * Kafka consumer thread, which could trigger rebalancing.
     * 
     * @param result the sentiment analysis result to persist
     * @return CompletableFuture that completes when the write succeeds or fails
     */
    @Async
    public CompletableFuture<Void> writeAsync(SentimentResult result) {
        var future = new CompletableFuture<Void>();
        var request = new WriteRequest(result, future);
        
        // Drop-and-log policy when queue is full
        var offered = writeQueue.offer(request);
        if (!offered) {
            log.warn("Write queue full (capacity: {}), dropping record for ticker {} tweet {}",
                queueCapacity, result.ticker(), result.tweetId());
            future.completeExceptionally(
                new IllegalStateException("Write queue at capacity, record dropped"));
            return future;
        }
        
        // Process the write immediately in this async thread
        processWriteQueue();
        
        return future;
    }

    /**
     * Processes pending write requests from the queue.
     * 
     * <p>Pulls records from the queue, routes to appropriate partition writers,
     * and handles file rotation based on record count and time thresholds.
     */
    private void processWriteQueue() {
        WriteRequest request;
        while ((request = writeQueue.poll()) != null) {
            try {
                var result = request.result();
                var writerKey = getWriterKey(result);
                var writer = getOrCreateWriter(result);
                
                // Buffer the record
                writer.buffer.add(result);
                writer.recordCount++;
                
                // Rotate file if thresholds exceeded
                if (shouldRotate(writer)) {
                    flushAndCloseWriter(writerKey);
                }
                
                request.future().complete(null);
            } catch (IOException e) {
                log.error("Failed to write Parquet record for ticker {}: {}",
                    request.result().ticker(), e.getMessage(), e);
                request.future().completeExceptionally(e);
            }
        }
    }

    /**
     * Determines if the current file should be rotated based on size or time thresholds.
     */
    private boolean shouldRotate(WriterState writer) {
        return writer.recordCount >= maxRecordsPerFile
            || Duration.between(writer.openedAt, Instant.now()).compareTo(MAX_FILE_DURATION) >= 0;
    }

    /**
     * Retrieves or creates a Parquet writer for the given result's partition.
     */
    private WriterState getOrCreateWriter(SentimentResult result) throws IOException {
        var key = getWriterKey(result);
        return activeWriters.computeIfAbsent(key, k -> {
            try {
                var pathStr = buildPartitionedPath(result);
                var file = new File(pathStr);
                
                log.info("Created Parquet writer for partition: {}", pathStr);
                return new WriterState(file, Instant.now());
            } catch (Exception e) {
                throw new RuntimeException("Failed to create Parquet writer", e);
            }
        });
    }

    /**
     * Builds a Spark-optimized partitioned path for the given sentiment result.
     */
    private String buildPartitionedPath(SentimentResult result) {
        var localDate = redditConverter.getLocalPartitionDate(result.originalTimestamp());
        var timestamp = System.currentTimeMillis();
        
        return String.format(
            "%s/ticker=%s/year=%d/month=%02d/day=%02d/sentiment-%d.parquet",
            basePath,
            result.ticker(),
            localDate.getYear(),
            localDate.getMonthValue(),
            localDate.getDayOfMonth(),
            timestamp
        );
    }

    /**
     * Generates a unique key for writer state tracking based on ticker and local date.
     */
    private String getWriterKey(SentimentResult result) {
        var localDate = redditConverter.getLocalPartitionDate(result.originalTimestamp());
        return String.format("%s-%s", result.ticker(), localDate);
    }

    /**
     * Flushes buffered records to disk and closes a specific Parquet writer.
     */
    private void flushAndCloseWriter(String writerKey) throws IOException {
        var state = activeWriters.remove(writerKey);
        if (state != null && !state.buffer.isEmpty()) {
            // Write buffered records using direct file I/O (no Hadoop security)
            var outputFile = new LocalOutputFile(state.file);
            
            try (var writer = SentimentResultParquetWriter.builder(outputFile, schema, 
                    CompressionCodecName.SNAPPY, ROW_GROUP_SIZE, PAGE_SIZE)) {
                for (var record : state.buffer) {
                    writer.write(record);
                }
            }
            
            log.info("Flushed and closed Parquet writer for key: {} ({} records written)",
                writerKey, state.recordCount);
        }
    }

    /**
     * Gracefully shuts down the writer, draining pending writes and closing all files.
     */
    @PreDestroy
    public void shutdown() {
        log.info("Shutting down ParquetSentimentWriter, draining {} pending writes", writeQueue.size());
        
        // Drain remaining writes
        processWriteQueue();
        
        // Flush and close all active writers
        activeWriters.keySet().forEach(key -> {
            try {
                flushAndCloseWriter(key);
            } catch (IOException e) {
                log.error("Error closing Parquet writer for key {}: {}", key, e.getMessage(), e);
            }
        });
        
        log.info("ParquetSentimentWriter shutdown complete");
    }

    /**
     * Internal record to track a write request with its completion future.
     */
    private record WriteRequest(SentimentResult result, CompletableFuture<Void> future) {}

    /**
     * Tracks the state of an active Parquet writer instance with buffered records.
     */
    private static class WriterState {
        final File file;
        final Instant openedAt;
        final List<SentimentResult> buffer;
        int recordCount;

        WriterState(File file, Instant openedAt) {
            this.file = file;
            this.openedAt = openedAt;
            this.buffer = new ArrayList<>();
            this.recordCount = 0;
        }
    }
}
