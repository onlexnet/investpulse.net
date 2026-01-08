package net.investpulse.reddit.infra.adapter;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostFetcher;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.util.*;

/**
 * Reddit API adapter using Spring RestClient.
 * Handles exponential backoff for 429 (rate limit) responses.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RedditApiAdapter implements RedditPostFetcher {

    private final RestClient restClient;

    @Value("${reddit.api.timeout-ms:10000}")
    private int timeoutMs;

    @Value("${reddit.api.max-retries:5}")
    private int maxRetries;

    private static final long INITIAL_BACKOFF_MS = 2000; // 2 seconds
    private static final long MAX_BACKOFF_MS = 30000;    // 30 seconds
    private static final double JITTER_FACTOR = 0.1;     // 10% jitter

    /**
     * Fetches Reddit posts for a ticker with exponential backoff on 429.
     */
    @Override
    public List<RawRedditPost> fetchPostsByTicker(String subreddit, String ticker) {
        String url = String.format("https://www.reddit.com/r/%s/search.json?q=%s&restrict_sr=1&limit=100",
                subreddit, ticker);

        int attempt = 0;
        while (attempt <= maxRetries) {
            try {
                return fetchWithRetry(url, subreddit, ticker);
            } catch (HttpStatusCodeException e) {
                if (e.getStatusCode().value() == 429) {
                    attempt++;
                    if (attempt > maxRetries) {
                        log.error("Max retries ({}) exceeded for subreddit={}, ticker={}", maxRetries, subreddit, ticker);
                        return Collections.emptyList();
                    }
                    long backoffMs = calculateBackoff(attempt);
                    log.warn("Rate limited (429) for r/{} ticker {}, backing off for {}ms (attempt {}/{})",
                            subreddit, ticker, backoffMs, attempt, maxRetries);
                    try {
                        Thread.sleep(backoffMs);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        log.warn("Backoff interrupted for r/{} ticker {}", subreddit, ticker);
                        return Collections.emptyList();
                    }
                } else {
                    log.error("HTTP error {} fetching r/{} ticker {}", e.getStatusCode(), subreddit, ticker);
                    return Collections.emptyList();
                }
            } catch (Exception e) {
                log.error("Error fetching r/{} ticker {}", subreddit, ticker, e);
                return Collections.emptyList();
            }
        }
        return Collections.emptyList();
    }

    /**
     * Performs the actual HTTP request and parses the response.
     */
    private List<RawRedditPost> fetchWithRetry(String url, String subreddit, String ticker) {
        var response = restClient
                .get()
                .uri(url)
                .retrieve()
                .body(RedditSearchResponse.class);

        if (response == null || response.data == null || response.data.children == null) {
            return Collections.emptyList();
        }

        List<RawRedditPost> posts = new ArrayList<>();
        for (RedditChild child : response.data.children) {
            if (child.data != null) {
                var post = mapToRawRedditPost(child.data, subreddit, ticker);
                posts.add(post);
            }
        }

        log.info("Fetched {} posts from r/{} for ticker {}", posts.size(), subreddit, ticker);
        return posts;
    }

    /**
     * Maps Reddit API response to RawRedditPost.
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
                Set.of(ticker)
        );
    }

    /**
     * Calculates exponential backoff with jitter.
     * Formula: min(2^attempt * INITIAL_BACKOFF, MAX_BACKOFF) × (1 + random jitter)
     */
    private long calculateBackoff(int attempt) {
        long exponentialBackoff = Math.min(
                (long) Math.pow(2, attempt) * INITIAL_BACKOFF_MS,
                MAX_BACKOFF_MS
        );
        double jitterAmount = exponentialBackoff * JITTER_FACTOR * Math.random();
        return exponentialBackoff + (long) jitterAmount;
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
