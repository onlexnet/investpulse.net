package net.investpulse.x.domain.port;

import net.investpulse.common.dto.RawTweet;

import java.util.List;

/**
 * Port interface for fetching tweets from external social media platforms.
 * Abstracts tweet fetching infrastructure from business logic.
 * <p>
 * This interface follows hexagonal architecture principles, allowing
 * the domain logic to remain independent of specific API implementations.
 */
public interface TweetFetcher {

    /**
     * Fetches tweets for a given username since a specific tweet ID.
     * <p>
     * Returns tweets in chronological order (oldest first). Implementations
     * should handle rate limiting, authentication, and error recovery.
     * 
     * @param username the Twitter/X username to fetch tweets from (without @ prefix)
     * @param sinceId the ID of the last processed tweet, or null to fetch recent tweets
     * @return list of raw tweets, empty if no new tweets are available
     * @throws RuntimeException if fetching fails after retries
     */
    List<RawTweet> fetchTweets(String username, String sinceId);
}
