package net.investpulse.reddit.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.reddit.metrics.RedditMetrics;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.util.Arrays;
import java.util.List;

/**
 * Scheduler for periodic Reddit post ingestion.
 * Polls configured tickers from subreddits at fixed intervals.
 */
@Slf4j
@Component
@ConditionalOnProperty(value = "reddit.scheduler.enabled", havingValue = "true", matchIfMissing = true)
@RequiredArgsConstructor
public class RedditIngestorScheduler {

    private final RedditIngestor redditIngestor;
    private final RedditMetrics redditMetrics;

    @Value("${reddit.tickers:AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA,META,AMD,COIN,MSTR}")
    private String tickersConfig;

    @Value("${reddit.poll-interval-seconds:5}")
    private int pollIntervalSeconds;

    @PostConstruct
    public void initializeMetrics() {
        log.info("Initializing Reddit metrics");
        redditMetrics.init();
    }

    /**
     * Scheduled task to ingest posts for all configured tickers.
     * Runs at fixed intervals (configurable via reddit.poll-interval-seconds).
     */
    @Scheduled(fixedDelayString = "${reddit.poll-interval-seconds:5}", timeUnit = java.util.concurrent.TimeUnit.SECONDS)
    public void scheduledIngestion() {
        List<String> tickers = parseTickers();
        log.debug("Starting scheduled ingestion for {} ticker(s)", tickers.size());

        for (String ticker : tickers) {
            try {
                redditIngestor.ingestPostsForTicker(ticker);
            } catch (Exception e) {
                log.error("Error during scheduled ingestion for ticker {}", ticker, e);
            }
        }
    }

    /**
     * Parses configured ticker list.
     */
    private List<String> parseTickers() {
        return Arrays.stream(tickersConfig.split(","))
                .map(String::trim)
                .filter(t -> !t.isEmpty())
                .toList();
    }
}
