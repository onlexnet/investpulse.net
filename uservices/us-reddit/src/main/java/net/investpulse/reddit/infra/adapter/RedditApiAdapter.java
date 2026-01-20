package net.investpulse.reddit.infra.adapter;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostFetcher;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Reddit API adapter using Spring RestClient.
 * Handles exponential backoff for 429 (rate limit) responses.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RedditApiAdapter implements RedditPostFetcher {

    // Sorts by newest posts first (sort=new) and limits to past week (t=week) for relevant sentiment tracking
    private static final String SEARCH_TEMPLATE = "https://www.reddit.com/r/%s/search.json?q=%s&restrict_sr=1&limit=100&sort=new&t=week";
    private static final long INITIAL_BACKOFF_MS = 2000; // 2 seconds
    private static final long MAX_BACKOFF_MS = 30000;    // 30 seconds
    private static final double JITTER_FACTOR = 0.1;     // 10% jitter

    private final RestClient restClient;

    @Value("${reddit.api.timeout-ms:10000}")
    private int timeoutMs;

    @Value("${reddit.api.max-retries:5}")
    private int maxRetries;

    /**
     * Fetches Reddit posts for a ticker with exponential backoff on 429.
     */
    @Override
    public List<RawRedditPost> fetchPostsByTicker(String subreddit, String ticker) {
        var url = String.format(SEARCH_TEMPLATE, subreddit, ticker);

        for (int attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return fetchPosts(url, subreddit, ticker);
            } catch (HttpStatusCodeException e) {
                if (e.getStatusCode().value() != 429) {
                    log.error("HTTP error {} fetching r/{} ticker {}", e.getStatusCode(), subreddit, ticker);
                    return List.of();
                }

                if (attempt == maxRetries) {
                    log.error("Max retries ({}) exceeded for subreddit={}, ticker={}", maxRetries, subreddit, ticker);
                    return List.of();
                }

                var backoff = calculateBackoff(attempt + 1);
                log.warn("Rate limited (429) for r/{} ticker {}, backing off for {}ms (attempt {}/{})",
                        subreddit, ticker, backoff.toMillis(), attempt + 1, maxRetries);

                if (!sleep(backoff)) {
                    log.warn("Backoff interrupted for r/{} ticker {}", subreddit, ticker);
                    return List.of();
                }
            } catch (Exception e) {
                log.error("Error fetching r/{} ticker {}", subreddit, ticker, e);
                return List.of();
            }
        }
        return List.of();
    }

    /**
     * Performs the actual HTTP request and parses the response.
     */
    private List<RawRedditPost> fetchPosts(String url, String subreddit, String ticker) {
        var response = restClient
                .get()
                .uri(url)
                .retrieve()
                .body(RedditSearchResponse.class);

        if (response == null || response.data == null || response.data.children == null) {
            return List.of();
        }

        var posts = response.data.children.stream()
                .map(RedditChild::data)
                .filter(Objects::nonNull)
                .map(child -> mapToRawRedditPost(child, subreddit, ticker))
                .toList();

        log.info("Fetched {} posts from r/{} for ticker {}", posts.size(), subreddit, ticker);
        return posts;
    }

    /**
     * Maps Reddit API response to RawRedditPost.
     * Note: version and lastUpdatedAt are set to null here and will be populated
     * by DatabaseDeduplicationService before publishing to Kafka.
     */
    private RawRedditPost mapToRawRedditPost(RedditPost data, String subreddit, String ticker) {
        return new RawRedditPost(
                data.id,
                data.title,
                data.selftext,
                data.score,
                data.num_comments,
                Instant.ofEpochSecond(data.created_utc),
                subreddit,
                Set.of(ticker),
                null,  // version will be set by DatabaseDeduplicationService
                null   // lastUpdatedAt will be set by DatabaseDeduplicationService
        );
    }

    /**
     * Calculates exponential backoff with jitter.
     * Formula: min(2^attempt * INITIAL_BACKOFF, MAX_BACKOFF) × (1 + random jitter)
     */
    private Duration calculateBackoff(int attempt) {
        var exponentialBackoff = Math.min(
                (long) Math.pow(2, attempt) * INITIAL_BACKOFF_MS,
                MAX_BACKOFF_MS
        );
        var jitterAmount = exponentialBackoff * JITTER_FACTOR * ThreadLocalRandom.current().nextDouble();
        return Duration.ofMillis(exponentialBackoff + (long) jitterAmount);
    }

    private boolean sleep(Duration backoff) {
        try {
            Thread.sleep(backoff.toMillis());
            return true;
        } catch (InterruptedException interruptedException) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    /**
     * JSON response models for Reddit Search API.
     */
    public record RedditSearchResponse(RedditData data) {}

    public record RedditData(List<RedditChild> children) {}

    public record RedditChild(RedditPost data) {}

    public record RedditPost(
            String id,
            String title,
            String selftext,
            int score,
            int num_comments,
            long created_utc
    ) {}
}
