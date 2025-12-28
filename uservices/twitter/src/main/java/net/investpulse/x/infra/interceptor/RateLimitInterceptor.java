package net.investpulse.x.infra.interceptor;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Rate limiting interceptor for Twitter API v2 requests.
 * Implements token bucket algorithm with 15 permits per 15-minute window.
 * <p>
 * This prevents exceeding Twitter's rate limits and handles 429 responses gracefully.
 */
@Slf4j
public class RateLimitInterceptor implements ClientHttpRequestInterceptor {

    private static final int MAX_REQUESTS_PER_WINDOW = 15;
    private static final long WINDOW_DURATION_MINUTES = 15;
    private static final String RATE_LIMIT_REMAINING_HEADER = "x-rate-limit-remaining";
    private static final String RATE_LIMIT_RESET_HEADER = "x-rate-limit-reset";
    private static final int LOW_REMAINING_THRESHOLD = 10;

    // Token bucket: stores available permits with automatic refresh
    private final Cache<String, AtomicInteger> permitBucket;

    public RateLimitInterceptor() {
        this.permitBucket = Caffeine.newBuilder()
                .expireAfterWrite(WINDOW_DURATION_MINUTES, TimeUnit.MINUTES)
                .build();
    }

    @Override
    public ClientHttpResponse intercept(
            HttpRequest request,
            byte[] body,
            ClientHttpRequestExecution execution) throws IOException {

        // Wait for available permit
        acquirePermit();

        // Execute request
        ClientHttpResponse response = execution.execute(request, body);

        // Log Twitter's rate limit status
        logRateLimitStatus(response);

        return response;
    }

    private void acquirePermit() {
        var bucket = permitBucket.get("twitter-api", key -> new AtomicInteger(MAX_REQUESTS_PER_WINDOW));
        
        while (true) {
            int available = bucket.get();
            
            if (available > 0) {
                if (bucket.compareAndSet(available, available - 1)) {
                    log.debug("Permit acquired. Remaining permits: {}", available - 1);
                    return;
                }
            } else {
                log.warn("Rate limit bucket exhausted. Waiting {} minutes for permits to refresh...", 
                        WINDOW_DURATION_MINUTES);
                try {
                    Thread.sleep(Duration.ofMinutes(1).toMillis());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Rate limit wait interrupted", e);
                }
                // Refresh bucket after waiting
                permitBucket.invalidate("twitter-api");
            }
        }
    }

    private void logRateLimitStatus(ClientHttpResponse response) {
        try {
            var remaining = response.getHeaders().getFirst(RATE_LIMIT_REMAINING_HEADER);
            var reset = response.getHeaders().getFirst(RATE_LIMIT_RESET_HEADER);

            if (remaining != null) {
                int remainingCount = Integer.parseInt(remaining);
                if (remainingCount < LOW_REMAINING_THRESHOLD) {
                    log.warn("Twitter API rate limit approaching: {} requests remaining (reset at: {})",
                            remainingCount, reset);
                } else {
                    log.debug("Twitter API rate limit status: {} requests remaining", remainingCount);
                }
            }
        } catch (Exception e) {
            log.debug("Unable to parse rate limit headers: {}", e.getMessage());
        }
    }
}
