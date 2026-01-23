# Reddit Service Metrics

Custom metrics have been added to the Reddit ingestor service for monitoring and observability via OpenTelemetry and Grafana.

## Available Metrics

### Counters (Cumulative)

These counters track the total number of operations:

| Metric Name | Description | Tags |
|---|---|---|
| `reddit.posts.published` | Total number of Reddit posts successfully published to Kafka | `service=reddit-ingestor` |
| `reddit.posts.fetched` | Total number of Reddit posts fetched from the Reddit API | `service=reddit-ingestor` |
| `reddit.posts.unchanged` | Total number of unchanged posts (deduplicated/skipped) | `service=reddit-ingestor` |
| `reddit.posts.updated` | Total number of posts with updates | `service=reddit-ingestor` |
| `reddit.publishing.errors` | Total number of errors during post publishing | `service=reddit-ingestor` |
| `reddit.fetching.errors` | Total number of errors during post fetching | `service=reddit-ingestor` |

### Timers (Latency/Duration)

These timers measure the duration of operations with percentiles (p50, p95, p99):

| Metric Name | Description | Tags | Percentiles |
|---|---|---|---|
| `reddit.ingestion.duration` | Time taken to ingest posts for a single ticker | `service=reddit-ingestor`, `ticker={TICKER}` | p50, p95, p99 |
| `reddit.sentiment.analysis.duration` | Time taken to analyze sentiment for a single post | `service=reddit-ingestor` | p50, p95 |
| `reddit.deduplication.duration` | Time taken to check and deduplicate a post | `service=reddit-ingestor` | p50, p95 |

### Gauges (Snapshots)

These gauges record snapshot values:

| Metric Name | Description |
|---|---|
| `reddit.posts.published.total` | Gauge of total published posts (snapshot) |
| `reddit.posts.fetched.total` | Gauge of total fetched posts (snapshot) |

## Configuration

Metrics are automatically exported via OpenTelemetry to the configured OTLP endpoint. Check `src/main/resources/application.yml`:

```yaml
management:
  tracing:
    sampling:
      probability: 1.0  # Adjust sampling as needed
  otlp:
    metrics:
      export:
        url: http://localhost:4318/v1/metrics  # Configure OTEL collector endpoint
        step: 10s  # Metric export interval
  metrics:
    export:
      otlp:
        enabled: true
    tags:
      application: reddit-ingestor
      service_namespace: investpulse
      environment: local
```

## Grafana Dashboard Examples

### Metric Queries

**Total Posts Published (Counter)**
```
rate(reddit_posts_published_total[1m])
```

**Ingestion Duration (Timer - p95)**
```
reddit_ingestion_duration_seconds{quantile="0.95"}
```

**Posts Fetched (Counter)**
```
increase(reddit_posts_fetched_total[5m])
```

**Error Rate**
```
rate(reddit_publishing_errors_total[1m]) + rate(reddit_fetching_errors_total[1m])
```

**Deduplication Efficiency**
```
(rate(reddit_posts_unchanged_total[1m]) / rate(reddit_posts_fetched_total[1m])) * 100
```

## Implementation Details

The metrics are implemented in [RedditMetrics.java](src/main/java/net/investpulse/reddit/metrics/RedditMetrics.java):

- **Initialization**: `@PostConstruct` method in `RedditIngestorScheduler` initializes all metrics
- **Recording**: Metrics are recorded in real-time during:
  - Post fetching operations
  - Deduplication checks
  - Sentiment analysis
  - Publication to Kafka

## Monitoring Recommendations

1. **Alert on Error Rates**: Set up alerts when `reddit.publishing.errors` or `reddit.fetching.errors` spike
2. **Monitor Latency**: Track `reddit.ingestion.duration` to detect performance degradation
3. **Track Deduplication**: Monitor the ratio of unchanged posts to identify cache effectiveness
4. **Throughput**: Use `reddit.posts.published` to monitor ingestion throughput

## Troubleshooting

If metrics don't appear in Grafana:

1. Ensure OTEL collector is running on the configured endpoint (`http://localhost:4318/v1/metrics`)
2. Check that `management.otlp.metrics.export.enabled: true` in `application.yml`
3. Verify the sampling probability is > 0 (default is 1.0)
4. Check application logs for any initialization errors related to metrics
5. Restart the Reddit service after configuration changes
