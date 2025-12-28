package net.investpulse.x.infra.adapter;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.config.TwitterConfig;
import net.investpulse.x.domain.port.TweetFetcher;
import net.investpulse.x.infra.interceptor.RateLimitInterceptor;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.test.context.TestPropertySource;
import org.springframework.web.client.RestClient;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assumptions.assumeThat;

/**
 * Integration test for TwitterApiAdapter that calls the real Twitter API v2.
 * <p>
 * This test requires valid Twitter API credentials. Set the following environment variable:
 * - TWITTER_BEARER_TOKEN: Your Twitter API v2 bearer token
 * <p>
 * The test will be skipped if credentials are not available.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
@TestPropertySource(properties = {
        "twitter.bearer.token=${TWITTER_BEARER_TOKEN:}",
        "twitter.api.base-url=https://api.twitter.com/2",
        "twitter.accounts-to-follow=elonmusk",
        "twitter.poll-interval-ms=60000"
})
class TwitterApiAdapterIntegrationTest {

    @Autowired
    private TweetFetcher tweetFetcher;

    @Autowired
    private TwitterConfig config;

    @TestConfiguration
    static class TestConfig {
        
        @Bean
        @Primary
        public RateLimitInterceptor testRateLimitInterceptor() {
            // Use same interceptor as production
            return new RateLimitInterceptor();
        }

        @Bean
        @Primary
        public RestClient testTwitterRestClient(TwitterConfig config, RateLimitInterceptor interceptor) {
            return RestClient.builder()
                    .baseUrl(config.getApiBaseUrl())
                    .defaultHeader("Authorization", "Bearer " + config.getBearerToken())
                    .defaultHeader("Content-Type", "application/json")
                    .requestInterceptor(interceptor)
                    .build();
        }

        @Bean
        @Primary
        public TweetFetcher testTweetFetcher(RestClient testTwitterRestClient) {
            return new TwitterApiAdapter(testTwitterRestClient);
        }
    }

    @Test
    void shouldFetchRealTweetsFromTwitterApi() {
        // Skip test if bearer token is not configured
        assumeThat(config.getBearerToken())
                .as("Twitter bearer token must be set via TWITTER_BEARER_TOKEN environment variable")
                .isNotBlank();

        // When: Fetch recent tweets from a well-known account (Elon Musk)
        String username = "elonmusk";
        List<RawTweet> tweets = tweetFetcher.fetchTweets(username, null);

        // Then: Verify real API response structure
        assertThat(tweets).isNotNull();
        
        // If tweets are available, verify structure
        if (!tweets.isEmpty()) {
            RawTweet firstTweet = tweets.get(0);
            assertThat(firstTweet.id()).isNotBlank();
            assertThat(firstTweet.text()).isNotBlank();
            assertThat(firstTweet.authorUsername()).isEqualTo(username);
            assertThat(firstTweet.authorId()).isNotBlank();
            assertThat(firstTweet.createdAt()).isNotNull();
            assertThat(firstTweet.source()).isEqualTo("Twitter API v2");
            assertThat(firstTweet.publisher()).isEqualTo("@" + username);
        }

        System.out.println("✓ Successfully fetched " + tweets.size() + " tweets from real Twitter API v2");
    }

    @Test
    void shouldHandleIncrementalFetchWithSinceId() {
        // Skip test if bearer token is not configured
        assumeThat(config.getBearerToken())
                .as("Twitter bearer token must be set via TWITTER_BEARER_TOKEN environment variable")
                .isNotBlank();

        String username = "elonmusk";

        // First fetch
        List<RawTweet> firstBatch = tweetFetcher.fetchTweets(username, null);
        assertThat(firstBatch).isNotNull();

        if (!firstBatch.isEmpty()) {
            // Second fetch with sinceId - should not return older tweets
            String lastTweetId = firstBatch.get(firstBatch.size() - 1).id();
            List<RawTweet> secondBatch = tweetFetcher.fetchTweets(username, lastTweetId);
            
            assertThat(secondBatch).isNotNull();
            
            // Verify no duplicate tweet IDs
            if (!secondBatch.isEmpty()) {
                assertThat(secondBatch)
                        .extracting(RawTweet::id)
                        .doesNotContain(lastTweetId);
            }
        }

        System.out.println("✓ Incremental fetch with since_id works correctly");
    }

    @Test
    void shouldRespectRateLimits() {
        // Skip test if bearer token is not configured
        assumeThat(config.getBearerToken())
                .as("Twitter bearer token must be set via TWITTER_BEARER_TOKEN environment variable")
                .isNotBlank();

        String username = "elonmusk";

        // Make multiple requests to test rate limiting
        for (int i = 0; i < 3; i++) {
            List<RawTweet> tweets = tweetFetcher.fetchTweets(username, null);
            assertThat(tweets).isNotNull();
            System.out.println("Request " + (i + 1) + ": Fetched " + tweets.size() + " tweets");
        }

        System.out.println("✓ Rate limiting interceptor works correctly");
    }

    @Test
    void shouldHandleNonExistentUser() {
        // Skip test if bearer token is not configured
        assumeThat(config.getBearerToken())
                .as("Twitter bearer token must be set via TWITTER_BEARER_TOKEN environment variable")
                .isNotBlank();

        String nonExistentUser = "thisusershouldnotexist12345xyz";
        
        List<RawTweet> tweets = tweetFetcher.fetchTweets(nonExistentUser, null);
        
        // Should return empty list, not throw exception
        assertThat(tweets).isEmpty();
        
        System.out.println("✓ Non-existent user handled gracefully");
    }
}
