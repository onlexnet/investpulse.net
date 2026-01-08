package net.investpulse.sentiment.persistence;

import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.SentimentResult;
import net.investpulse.sentiment.converter.RedditPostConverter;
import net.investpulse.sentiment.schema.SentimentResultSchema;
import org.apache.avro.generic.GenericRecord;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Async Parquet writer for {@link SentimentResult} records with Spark-optimized partitioning.
 * 
 * <p><strong>Architecture:</strong>
 * <ul>
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
    
    private final SentimentResultSchema schema;
    private final RedditPostConverter redditConverter;
    private LinkedBlockingQueue<WriteRequest> writeQueue;
    private final Map<String, WriterState> activeWriters = new ConcurrentHashMap<>();
    private final Configuration hadoopConfig;

    public ParquetSentimentWriter(SentimentResultSchema schema, RedditPostConverter redditConverter) {
        this.schema = schema;
        this.redditConverter = redditConverter;
        this.hadoopConfig = createHadoopConfig();
    }

    /**
     * Initializes the write queue with configured capacity after dependency injection.
     */
    @PostConstruct
    public void init() {
        this.writeQueue = new LinkedBlockingQueue<>(queueCapacity);
        log.info("Initialized ParquetSentimentWriter with queue capacity: {}, base path: {}",
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
     * <p><strong>TODO:</strong> Consider adding metrics (dropped record counter) for monitoring.
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
                
                var avroRecord = schema.toAvroRecord(result);
                writer.writer.write(avroRecord);
                writer.recordCount++;
                
                // Rotate file if thresholds exceeded
                if (shouldRotate(writer)) {
                    closeWriter(writerKey);
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
     * 
     * <p><strong>Rotation Triggers:</strong>
     * <ul>
     *   <li>Record count exceeds {@code max-records-per-file} (default 1000)</li>
     *   <li>File has been open for more than {@code MAX_FILE_DURATION} (5 minutes)</li>
     * </ul>
     * 
     * @param writer the current writer state
     * @return true if rotation should occur
     */
    private boolean shouldRotate(WriterState writer) {
        return writer.recordCount >= maxRecordsPerFile
            || Duration.between(writer.openedAt, Instant.now()).compareTo(MAX_FILE_DURATION) >= 0;
    }

    /**
     * Retrieves or creates a Parquet writer for the given result's partition.
     * 
     * <p>Partition structure: {@code ticker=SYMBOL/year=YYYY/month=MM/day=DD/}
     * Directories are created automatically if they don't exist.
     * 
     * @param result the sentiment result to determine partition
     * @return active writer for this partition
     * @throws IOException if writer creation or directory creation fails
     */
    private WriterState getOrCreateWriter(SentimentResult result) throws IOException {
        var key = getWriterKey(result);
        return activeWriters.computeIfAbsent(key, k -> {
            try {
                var path = buildPartitionedPath(result);
                
                // Create parent directories automatically
                var file = new java.io.File(path.getParent().toString());
                if (!file.exists()) {
                    var created = file.mkdirs();
                    if (!created) {
                        throw new IOException("Failed to create directory: " + file);
                    }
                }
                
                var writer = AvroParquetWriter.<GenericRecord>builder(path)
                    .withSchema(schema.getSchema())
                    .withConf(hadoopConfig)
                    .withCompressionCodec(CompressionCodecName.SNAPPY)
                    .withRowGroupSize(ROW_GROUP_SIZE)
                    .withPageSize(PAGE_SIZE)
                    .build();
                
                log.info("Created Parquet writer for partition: {}", path);
                return new WriterState(writer, Instant.now());
            } catch (IOException e) {
                throw new RuntimeException("Failed to create Parquet writer", e);
            }
        });
    }

    /**
     * Builds a Spark-optimized partitioned path for the given sentiment result.
     * 
     * <p><strong>Path Format:</strong>
     * {@code /data/sentiment/ticker=AAPL/year=2025/month=12/day=26/sentiment-1735234567890.parquet}
     * 
     * <p><strong>Date Calculation:</strong>
     * Partition dates are derived from {@code originalTimestamp} (source creation time in UTC)
     * converted to the configured local timezone. This ensures posts are partitioned by
     * the local business date they occurred, not UTC date.
     * 
     * <p>Example: A Reddit post created 2026-01-07 23:00 UTC in timezone UTC+5:00
     * is converted to 2026-01-08 04:00 local time, and partitioned as day=08.
     * 
     * <p>This structure enables efficient Spark partition pruning:
     * <pre>spark.read.parquet("/data/sentiment")
     *   .filter("ticker = 'AAPL' AND year = 2025 AND month = 12")</pre>
     * 
     * @param result the sentiment result to partition
     * @return Hadoop Path with partitioning structure
     */
    private Path buildPartitionedPath(SentimentResult result) {
        // Use local date calculated from original source timestamp
        var localDate = redditConverter.getLocalPartitionDate(result.originalTimestamp());
        var timestamp = System.currentTimeMillis();
        
        var filename = String.format(
            "%s/ticker=%s/year=%d/month=%02d/day=%02d/sentiment-%d.parquet",
            basePath,
            result.ticker(),
            localDate.getYear(),
            localDate.getMonthValue(),
            localDate.getDayOfMonth(),
            timestamp
        );
        
        return new Path(filename);
    }

    /**
     * Generates a unique key for writer state tracking based on ticker and local date.
     * 
     * <p>Writers are pooled per (ticker, local-date) to avoid reopening the same partition.
     * Local date is calculated from {@code originalTimestamp} using configured timezone.
     * 
     * @param result the sentiment result
     * @return unique key string (e.g., "AAPL-2025-12-26")
     */
    private String getWriterKey(SentimentResult result) {
        var localDate = redditConverter.getLocalPartitionDate(result.originalTimestamp());
        return String.format("%s-%s", result.ticker(), localDate);
    }

    /**
     * Closes a specific Parquet writer and removes it from the active pool.
     * 
     * @param writerKey the unique writer key
     */
    private void closeWriter(String writerKey) {
        var state = activeWriters.remove(writerKey);
        if (state != null) {
            try {
                state.writer.close();
                log.info("Closed Parquet writer for key: {} ({} records written)",
                    writerKey, state.recordCount);
            } catch (IOException e) {
                log.error("Error closing Parquet writer for key {}: {}", writerKey, e.getMessage(), e);
            }
        }
    }

    /**
     * Creates Hadoop configuration optimized for streaming Parquet writes.
     * 
     * <p>Key settings:
     * <ul>
     *   <li>Reduced block size (8MB) for faster flushes vs default 128MB</li>
     *   <li>Smaller page size (1MB) for better streaming performance</li>
     *   <li>Dictionary encoding enabled for compression efficiency</li>
     * </ul>
     * 
     * @return configured Hadoop Configuration instance
     */
    private Configuration createHadoopConfig() {
        var conf = new Configuration();
        conf.setInt("parquet.block.size", ROW_GROUP_SIZE);
        conf.setInt("parquet.page.size", PAGE_SIZE);
        conf.setBoolean("parquet.enable.dictionary", true);
        return conf;
    }

    /**
     * Gracefully shuts down the writer, draining pending writes and closing all files.
     * 
     * <p><strong>Shutdown Sequence:</strong>
     * <ol>
     *   <li>Process all pending records in the write queue</li>
     *   <li>Close all active Parquet writers</li>
     *   <li>Log final statistics</li>
     * </ol>
     * 
     * <p>Invoked automatically by Spring on application shutdown via {@code @PreDestroy}.
     */
    @PreDestroy
    public void shutdown() {
        log.info("Shutting down ParquetSentimentWriter, draining {} pending writes", writeQueue.size());
        
        // Drain remaining writes
        processWriteQueue();
        
        // Close all active writers
        activeWriters.keySet().forEach(this::closeWriter);
        
        log.info("ParquetSentimentWriter shutdown complete");
    }

    /**
     * Internal record to track a write request with its completion future.
     */
    private record WriteRequest(SentimentResult result, CompletableFuture<Void> future) {}

    /**
     * Tracks the state of an active Parquet writer instance.
     */
    private static class WriterState {
        final ParquetWriter<GenericRecord> writer;
        final Instant openedAt;
        int recordCount;

        WriterState(ParquetWriter<GenericRecord> writer, Instant openedAt) {
            this.writer = writer;
            this.openedAt = openedAt;
            this.recordCount = 0;
        }
    }
}
