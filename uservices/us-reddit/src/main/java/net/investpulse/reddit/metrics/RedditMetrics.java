package net.investpulse.reddit.metrics;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/**
 * Custom metrics for Reddit ingestion service.
 * Tracks post fetching, publishing, deduplication, and sentiment analysis.
 * Metrics are exported via OpenTelemetry and visible in Grafana.
 */
@Component
@RequiredArgsConstructor
public class RedditMetrics {

    private final MeterRegistry meterRegistry;

    // Counters for post processing
    private Counter postsPublishedCounter;
    private Counter postsFetchedCounter;
    private Counter postsUnchangedCounter;
    private Counter postsUpdatedCounter;
    private Counter publishingErrorsCounter;
    private Counter fetchingErrorsCounter;

    // Timers for performance tracking
    private Timer ingestionTimer;
    private Timer sentimentAnalysisTimer;
    private Timer deduplicationTimer;

    public void init() {
        // Initialize counters
        postsPublishedCounter = Counter.builder("reddit.posts.published")
                .description("Total number of Reddit posts published to Kafka")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        postsFetchedCounter = Counter.builder("reddit.posts.fetched")
                .description("Total number of Reddit posts fetched from API")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        postsUnchangedCounter = Counter.builder("reddit.posts.unchanged")
                .description("Total number of unchanged posts (skipped)")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        postsUpdatedCounter = Counter.builder("reddit.posts.updated")
                .description("Total number of posts with updates")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        publishingErrorsCounter = Counter.builder("reddit.publishing.errors")
                .description("Total number of errors during post publishing")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        fetchingErrorsCounter = Counter.builder("reddit.fetching.errors")
                .description("Total number of errors during post fetching")
                .tag("service", "reddit-ingestor")
                .register(meterRegistry);

        // Initialize timers
        ingestionTimer = Timer.builder("reddit.ingestion.duration")
                .description("Time taken to ingest posts for a single ticker")
                .tag("service", "reddit-ingestor")
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(meterRegistry);

        sentimentAnalysisTimer = Timer.builder("reddit.sentiment.analysis.duration")
                .description("Time taken to analyze sentiment for a single post")
                .tag("service", "reddit-ingestor")
                .publishPercentiles(0.5, 0.95)
                .register(meterRegistry);

        deduplicationTimer = Timer.builder("reddit.deduplication.duration")
                .description("Time taken to check and deduplicate a post")
                .tag("service", "reddit-ingestor")
                .publishPercentiles(0.5, 0.95)
                .register(meterRegistry);
    }

    // Counter recording methods
    public void recordPostPublished() {
        postsPublishedCounter.increment();
    }

    public void recordPostFetched(int count) {
        postsFetchedCounter.increment(count);
    }

    public void recordPostUnchanged(int count) {
        postsUnchangedCounter.increment(count);
    }

    public void recordPostUpdated(int count) {
        postsUpdatedCounter.increment(count);
    }

    public void recordPublishingError() {
        publishingErrorsCounter.increment();
    }

    public void recordFetchingError() {
        fetchingErrorsCounter.increment();
    }

    // Timer recording methods
    public Timer.Sample startIngestionTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordIngestionTime(Timer.Sample sample, String ticker) {
        sample.stop(Timer.builder("reddit.ingestion.duration")
                .description("Time taken to ingest posts for a single ticker")
                .tag("service", "reddit-ingestor")
                .tag("ticker", ticker)
                .publishPercentiles(0.5, 0.95, 0.99)
                .register(meterRegistry));
    }

    public Timer.Sample startSentimentAnalysisTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordSentimentAnalysisTime(Timer.Sample sample) {
        sample.stop(sentimentAnalysisTimer);
    }

    public Timer.Sample startDeduplicationTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordDeduplicationTime(Timer.Sample sample) {
        sample.stop(deduplicationTimer);
    }

    // Gauge - records a snapshot value (call periodically)
    public void recordPublishedPostsGauge(long value) {
        meterRegistry.gauge("reddit.posts.published.total", value);
    }

    public void recordFetchedPostsGauge(long value) {
        meterRegistry.gauge("reddit.posts.fetched.total", value);
    }
}
