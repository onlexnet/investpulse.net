package net.investpulse.x.infra.adapter;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.TweetFetcher;
import org.springframework.http.HttpStatusCode;
import org.springframework.web.client.RestClient;

import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Set;

/**
 * Adapter implementation for fetching tweets from Twitter API v2.
 * Uses RestClient for synchronous HTTP communication.
 * <p>
 * Handles authentication, response parsing, and error recovery.
 * Rate limiting is managed by {@link net.investpulse.x.infra.interceptor.RateLimitInterceptor}.
 */
@Slf4j
@RequiredArgsConstructor
public class TwitterApiAdapter implements TweetFetcher {

    private static final String USER_LOOKUP_ENDPOINT = "/users/by/username/{username}";
    private static final String USER_TWEETS_ENDPOINT = "/users/{userId}/tweets";
    private static final String TWEET_FIELDS = "id,text,created_at,author_id";
    private static final int MAX_RESULTS = 10;

    private final RestClient restClient;

    @Override
    public List<RawTweet> fetchTweets(String username, String sinceId) {
        log.debug("Fetching tweets for username: {} since ID: {}", username, sinceId);

        try {
            // Step 1: Get user ID from username
            String userId = fetchUserId(username);
            if (userId == null) {
                log.warn("User not found: {}", username);
                return Collections.emptyList();
            }

            // Step 2: Fetch tweets for user ID
            return fetchTweetsForUserId(userId, username, sinceId);

        } catch (Exception e) {
            log.error("Error fetching tweets for {}: {}", username, e.getMessage(), e);
            throw new RuntimeException("Failed to fetch tweets for " + username, e);
        }
    }

    private String fetchUserId(String username) {
        var response = restClient.get()
                .uri(USER_LOOKUP_ENDPOINT, username)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, (request, resp) -> {
                    log.error("Client error fetching user {}: {}", username, resp.getStatusCode());
                    throw new RuntimeException("User lookup failed: " + resp.getStatusCode());
                })
                .onStatus(HttpStatusCode::is5xxServerError, (request, resp) -> {
                    log.error("Server error fetching user {}: {}", username, resp.getStatusCode());
                    throw new RuntimeException("Twitter API server error: " + resp.getStatusCode());
                })
                .body(UserLookupResponse.class);

        return response != null && response.data() != null ? response.data().id() : null;
    }

    private List<RawTweet> fetchTweetsForUserId(String userId, String username, String sinceId) {
        var uriSpec = restClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path(USER_TWEETS_ENDPOINT)
                        .queryParam("tweet.fields", TWEET_FIELDS)
                        .queryParam("max_results", MAX_RESULTS)
                        .queryParamIfPresent("since_id", java.util.Optional.ofNullable(sinceId))
                        .build(userId));

        var response = uriSpec
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, (request, resp) -> {
                    log.error("Client error fetching tweets for user {}: {}", username, resp.getStatusCode());
                    throw new RuntimeException("Tweet fetch failed: " + resp.getStatusCode());
                })
                .onStatus(HttpStatusCode::is5xxServerError, (request, resp) -> {
                    log.error("Server error fetching tweets for user {}: {}", username, resp.getStatusCode());
                    throw new RuntimeException("Twitter API server error: " + resp.getStatusCode());
                })
                .body(TweetResponse.class);

        if (response == null || response.data() == null) {
            log.debug("No tweets found for user {}", username);
            return Collections.emptyList();
        }

        return response.data().stream()
                .map(tweet -> new RawTweet(
                        tweet.id(),
                        tweet.text(),
                        tweet.authorId(),
                        username,
                        parseInstant(tweet.createdAt()),
                        "Twitter API v2",
                        "@" + username,
                        Set.of() // Tickers extracted later by TickerExtractor
                ))
                .toList();
    }

    private Instant parseInstant(String timestamp) {
        try {
            return timestamp != null ? Instant.parse(timestamp) : Instant.now();
        } catch (Exception e) {
            log.warn("Failed to parse timestamp: {}", timestamp);
            return Instant.now();
        }
    }

    // DTO for Twitter API v2 user lookup response
    @JsonIgnoreProperties(ignoreUnknown = true)
    record UserLookupResponse(@JsonProperty("data") UserData data) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record UserData(@JsonProperty("id") String id, @JsonProperty("username") String username) {}

    // DTO for Twitter API v2 tweets response
    @JsonIgnoreProperties(ignoreUnknown = true)
    record TweetResponse(@JsonProperty("data") List<TweetData> data) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record TweetData(
            @JsonProperty("id") String id,
            @JsonProperty("text") String text,
            @JsonProperty("author_id") String authorId,
            @JsonProperty("created_at") String createdAt
    ) {}
}
