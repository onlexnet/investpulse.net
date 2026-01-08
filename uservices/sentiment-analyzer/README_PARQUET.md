# Parquet Persistence for Sentiment Analysis

## Overview

The `sentiment-analyzer` service now persists `SentimentResult` records to Parquet files optimized for Apache Spark analytics. This dual-write architecture publishes sentiment results to both:
1. **Kafka topic** `sentiment-aggregated` (real-time streaming)
2. **Parquet files** (batch analytics, historical queries)

## Architecture

### Key Components

- **`SentimentResultSchema`**: Avro schema definition for `SentimentResult` Java Records
- **`ParquetSentimentWriter`**: Async Parquet writer with bounded queue and file rotation
- **`SentimentAggregator`**: Kafka consumer with manual offset management tied to Parquet write confirmation

### Data Flow

```
Kafka ticker-* → SentimentAggregator → [Kafka publish, Parquet queue]
                                              ↓              ↓
                                    sentiment-aggregated  ParquetWriter
                                                              ↓
                                          /data/sentiment/ticker=AAPL/...
                                                              ↓
                                          Offset committed ✓
```

### File Structure

```
/data/sentiment/
├── ticker=AAPL/
│   ├── year=2025/
│   │   ├── month=12/
│   │   │   ├── day=26/
│   │   │   │   ├── sentiment-1735234567890.parquet
│   │   │   │   └── sentiment-1735234789012.parquet
├── ticker=TSLA/
│   ├── year=2025/
│   │   ├── month=12/
│   │   │   ├── day=26/
│   │   │   │   └── sentiment-1735234890123.parquet
```

## Configuration

### application.yml

```yaml
sentiment:
  parquet:
    # Base directory for partitioned Parquet files
    base-path: /data/sentiment
    
    # File rotation: create new file after N records
    max-records-per-file: 1000
    
    # Bounded queue capacity (drop-and-log when full)
    queue-capacity: 10000

spring:
  kafka:
    consumer:
      # Manual commit: offsets committed AFTER Parquet write succeeds
      enable-auto-commit: false
      
      # Adjusted for Parquet rotation (500 records * 2 = ~1 file per 2 batches)
      max-poll-records: 500
      
      properties:
        # Increase poll interval to account for Parquet write latency
        max.poll.interval.ms: 600000  # 10 minutes
```

### Environment Variables

For production deployment, ensure the base path exists or is writable:

```bash
# Docker/K8s volume mount
volumes:
  - /mnt/analytics:/data/sentiment

# Or environment override
environment:
  SENTIMENT_PARQUET_BASE_PATH: /mnt/analytics/sentiment
```

## Operational Behavior

### At-Least-Once Delivery Guarantee

Kafka offsets are committed **only after** Parquet write completes successfully. If the write fails:
1. Offset is NOT acknowledged
2. Kafka will redeliver the message after consumer rebalancing
3. This may result in duplicate records in Parquet (acceptable for analytics)

### Drop-and-Log Queue Policy

When the write queue reaches capacity (default 10,000):
- New records are **dropped** (not written to Parquet)
- A WARN log is emitted with ticker and tweet ID
- Kafka offset is still committed (to prevent infinite redelivery)
- **TODO**: Add metrics (counter) for dropped records

### File Rotation

Files are rotated when either threshold is met:
1. **Record count**: 1,000 records per file (configurable)
2. **Time duration**: 5 minutes open (hardcoded in `ParquetSentimentWriter`)

Rotation creates a new file in the same partition with a new timestamp suffix.

### Graceful Shutdown

On application shutdown (`@PreDestroy`):
1. Drain pending writes from queue
2. Close all open Parquet writers
3. Log final statistics

## Spark Integration

### Reading Parquet Files

```scala
// Read all sentiment data
val df = spark.read.parquet("/data/sentiment")

// Partition pruning for efficient queries
val appleToday = spark.read.parquet("/data/sentiment")
  .filter($"ticker" === "AAPL" && $"year" === 2025 && $"month" === 12 && $"day" === 26)

// Time-series aggregation
val dailySentiment = spark.read.parquet("/data/sentiment")
  .groupBy($"ticker", $"year", $"month", $"day", $"sentiment")
  .agg(count("*").as("count"), avg("score").as("avg_score"))
  .orderBy($"ticker", $"year", $"month", $"day")
```

### Schema

```scala
root
 |-- tweetId: string (nullable = false)
 |-- ticker: string (nullable = false)
 |-- score: double (nullable = false)
 |-- sentiment: string (nullable = false)  // "POSITIVE", "NEGATIVE", "NEUTRAL"
 |-- processedAt: long (nullable = false)  // epoch milliseconds
 |-- publisher: string (nullable = false)
 |-- source: string (nullable = false)
```

**Note**: `processedAt` is stored as `long` (epoch milliseconds), losing nanosecond precision from `Instant`. To convert back:

```scala
import org.apache.spark.sql.functions._

val dfWithTimestamp = df
  .withColumn("processedAtTs", (col("processedAt") / 1000).cast("timestamp"))
```

## Performance Tuning

### Hadoop Configuration

Parquet writer uses optimized settings for streaming workloads:
- **Row group size**: 8MB (vs default 128MB) for faster flushes
- **Page size**: 1MB for better streaming performance
- **Compression**: Snappy (fast compression, decent ratio)

### Kafka Consumer Tuning

```yaml
spring:
  kafka:
    consumer:
      # Fetch more records per poll to amortize Parquet write latency
      max-poll-records: 500
      
      properties:
        # Larger batches reduce per-message overhead
        fetch.min.bytes: 1024
        fetch.max.wait.ms: 500
        
        # Allow longer processing time (Parquet writes can be slow)
        max.poll.interval.ms: 600000  # 10 min
```

### Back-Pressure Monitoring

If consumers are lagging, check:
1. **Queue utilization**: `writeQueue.size()` should stay below capacity
2. **File I/O latency**: Slow disk can cause queue buildup
3. **Consumer lag**: Kafka metrics for `records-lag-max`

**TODO**: Expose metrics for:
- `parquet.queue.size` (gauge)
- `parquet.records.dropped` (counter)
- `parquet.files.created` (counter)
- `parquet.write.latency` (histogram)

## Testing

### Unit Tests

- `SentimentAggregatorTest`: Mocks Parquet writer to test Kafka integration
- `FinancialSentimentServiceTest`: NLP sentiment scoring logic

### Integration Tests

- `ParquetSentimentWriterIntegrationTest`: **Disabled** due to Hadoop + Java 25 compatibility

The integration tests are disabled because Hadoop's `UserGroupInformation` API conflicts with Java 25's restricted `javax.security.auth.Subject`. In production, the service runs with:

```bash
java --enable-native-access=ALL-UNNAMED \
     --add-opens java.base/javax.security.auth=ALL-UNNAMED \
     -jar sentiment-analyzer.jar
```

This is configured automatically in Spring Boot's startup.

## Troubleshooting

### Issue: "Write queue full, dropping record"

**Cause**: Parquet writes are slower than Kafka consumption rate

**Solutions**:
1. Increase `queue-capacity` (default 10,000)
2. Reduce `max-poll-records` to slow consumption
3. Optimize disk I/O (use SSD, increase IOPS)
4. Reduce `max-records-per-file` to rotate files faster

### Issue: Consumer rebalancing frequently

**Cause**: Parquet write latency exceeds `max.poll.interval.ms`

**Solutions**:
1. Increase `max.poll.interval.ms` (default 600s)
2. Reduce `max-poll-records` per batch
3. Monitor `parquet.write.latency` metrics

### Issue: Duplicate records in Parquet

**Cause**: At-least-once delivery semantics

**Explanation**: If a Parquet write succeeds but the service crashes before committing the Kafka offset, the message will be redelivered and written again after restart.

**Solutions**:
1. **Deduplicate in Spark**: Use `dropDuplicates("tweetId")` when reading
2. **Accept duplicates**: For aggregations (counts, averages), duplicates have minimal impact
3. **Exactly-once semantics**: Requires transactional Kafka + idempotent Parquet writes (complex)

### Issue: Files not created

**Cause**: Missing directory permissions or invalid base path

**Solutions**:
1. Ensure `/data/sentiment` exists and is writable
2. Check logs for `IOException` or `FileNotFoundException`
3. Verify Docker volume mounts or Kubernetes PVC bindings

### Issue: "UnsupportedOperationException: getSubject is not supported" (Java 18+)

**Cause**: Hadoop's `UserGroupInformation` tries to use deprecated `Subject.getSubject()` API

**Error**:
```
java.lang.UnsupportedOperationException: getSubject is not supported
    at javax.security.auth.Subject.getSubject(Subject.java:277)
    at org.apache.hadoop.security.UserGroupInformation.getCurrentUser(...)
```

**Solutions**:
✅ **Implemented Fix**: Hadoop configuration now sets `hadoop.security.authentication=simple` in `ParquetSentimentWriter.createHadoopConfig()`, which bypasses the problematic Subject API call.

**Alternative fixes** (if the above doesn't work):
1. **JVM argument**: Add `-Djava.security.manager=allow` to enable legacy Subject behavior
2. **Module opens**: Add `--add-opens java.base/javax.security.auth=ALL-UNNAMED`
3. **Downgrade Java**: Use Java 17 LTS (not recommended)

**References**: [HADOOP-19246](https://issues.apache.org/jira/browse/HADOOP-19246)

## Future Enhancements

### TODO Items

1. **Timeout for Parquet writes**: Add configurable timeout (30s) to prevent consumer thread starvation
   ```java
   parquetWriter.writeAsync(result).get(30, TimeUnit.SECONDS);
   ```

2. **Metrics and monitoring**: Expose Micrometer metrics for queue size, dropped records, write latency

3. **Circuit breaker**: Temporarily disable Parquet writes during file system failures to maintain Kafka throughput

4. **S3/Azure Blob integration**: Support writing directly to cloud storage instead of local filesystem

5. **Schema evolution**: Add Avro schema registry integration for backward-compatible field additions

6. **Compaction**: Background job to merge small Parquet files into larger optimized files

## References

- [Apache Parquet Documentation](https://parquet.apache.org/docs/)
- [Spark Parquet Data Source](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html)
- [Hadoop + Java 25 Compatibility](https://issues.apache.org/jira/browse/HADOOP-19246)
- [Spring Kafka Manual Commit](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/listener-annotation.html#manual-assignment)
