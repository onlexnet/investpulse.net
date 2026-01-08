package net.investpulse.reddit.infra.cache;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * Caffeine-based cache for tracking processed Reddit post IDs.
 * Prevents duplicate processing of posts within a 12-hour window.
 */
@Slf4j
@Component
public class PostDeduplicationCache {

    private final Cache<String, Boolean> cache;

    public PostDeduplicationCache(
            @Value("${reddit.cache.ttl-hours:12}") int ttlHours,
            @Value("${reddit.cache.max-entries:10000}") int maxEntries) {
        this.cache = Caffeine.newBuilder()
                .expireAfterWrite(ttlHours, TimeUnit.HOURS)
                .maximumSize(maxEntries)
                .build();
        
        log.info("Initialized PostDeduplicationCache with TTL={}h, maxEntries={}", ttlHours, maxEntries);
    }

    /**
     * Checks if a post ID has already been processed.
     *
     * @param postId the Reddit post ID
     * @return true if post was already processed, false otherwise
     */
    public boolean isDuplicate(String postId) {
        return cache.getIfPresent(postId) != null;
    }

    /**
     * Marks a post ID as processed.
     *
     * @param postId the Reddit post ID
     */
    public void markAsProcessed(String postId) {
        cache.put(postId, true);
    }

    /**
     * Returns the approximate cache size.
     */
    public long getSize() {
        return cache.estimatedSize();
    }

    /**
     * Clears the entire cache.
     */
    public void clear() {
        cache.invalidateAll();
        log.info("Cleared PostDeduplicationCache");
    }
}
