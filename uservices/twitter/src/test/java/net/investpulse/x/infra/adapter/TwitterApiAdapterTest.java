package net.investpulse.x.infra.adapter;

import net.investpulse.common.dto.RawTweet;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.function.Function;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TwitterApiAdapterTest {

    @Mock
    private RestClient restClient;

    @Mock
    private RestClient.RequestHeadersUriSpec requestHeadersUriSpec;

    @Mock
    private RestClient.ResponseSpec responseSpec;

    private TwitterApiAdapter adapter;

    @BeforeEach
    void setUp() {
        adapter = new TwitterApiAdapter(restClient);
    }

    @Test
    void shouldFetchTweetsSuccessfully() {
        // Given
        String username = "testuser";
        String sinceId = "123456789";

        // Mock user lookup
        when(restClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(anyString(), (Object[]) any())).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.onStatus(any(), any())).thenReturn(responseSpec);
        
        // First call returns user lookup response
        when(responseSpec.body(TwitterApiAdapter.UserLookupResponse.class))
                .thenReturn(new TwitterApiAdapter.UserLookupResponse(
                        new TwitterApiAdapter.UserData("987654321", "testuser")
                ));

        // Mock tweets fetch - second set of calls
        when(requestHeadersUriSpec.uri(any(Function.class))).thenReturn(requestHeadersUriSpec);
        
        // Second call returns tweets response
        var tweetData1 = new TwitterApiAdapter.TweetData("111", "Test tweet about $AAPL", 
                "987654321", "2025-12-27T10:00:00.000Z");
        var tweetData2 = new TwitterApiAdapter.TweetData("222", "Another tweet about $TSLA", 
                "987654321", "2025-12-27T11:00:00.000Z");
        when(responseSpec.body(TwitterApiAdapter.TweetResponse.class))
                .thenReturn(new TwitterApiAdapter.TweetResponse(List.of(tweetData1, tweetData2)));

        // When
        List<RawTweet> tweets = adapter.fetchTweets(username, sinceId);

        // Then
        assertThat(tweets).hasSize(2);
        assertThat(tweets.get(0).id()).isEqualTo("111");
        assertThat(tweets.get(0).text()).contains("$AAPL");
        assertThat(tweets.get(0).authorUsername()).isEqualTo(username);
        assertThat(tweets.get(1).id()).isEqualTo("222");
        assertThat(tweets.get(1).text()).contains("$TSLA");
    }

    @Test
    void shouldReturnEmptyListWhenUserNotFound() {
        // Given
        String username = "nonexistent";

        when(restClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(anyString(), (Object[]) any())).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.onStatus(any(), any())).thenReturn(responseSpec);
        when(responseSpec.body(TwitterApiAdapter.UserLookupResponse.class)).thenReturn(null);

        // When
        List<RawTweet> tweets = adapter.fetchTweets(username, null);

        // Then
        assertThat(tweets).isEmpty();
    }

    @Test
    void shouldReturnEmptyListWhenNoTweetsAvailable() {
        // Given
        String username = "testuser";

        // Mock user lookup
        when(restClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(anyString(), (Object[]) any())).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.onStatus(any(), any())).thenReturn(responseSpec);
        when(responseSpec.body(TwitterApiAdapter.UserLookupResponse.class))
                .thenReturn(new TwitterApiAdapter.UserLookupResponse(
                        new TwitterApiAdapter.UserData("987654321", "testuser")
                ));

        // Mock tweets fetch with empty data
        when(requestHeadersUriSpec.uri(any(Function.class))).thenReturn(requestHeadersUriSpec);
        when(responseSpec.body(TwitterApiAdapter.TweetResponse.class)).thenReturn(null);

        // When
        List<RawTweet> tweets = adapter.fetchTweets(username, null);

        // Then
        assertThat(tweets).isEmpty();
    }

    @Test
    void shouldThrowExceptionOnApiError() {
        // Given
        String username = "testuser";

        when(restClient.get()).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.uri(anyString(), (Object[]) any())).thenReturn(requestHeadersUriSpec);
        when(requestHeadersUriSpec.retrieve()).thenReturn(responseSpec);
        when(responseSpec.onStatus(any(), any())).thenAnswer(invocation -> {
            // Simulate 401 error
            throw new RuntimeException("User lookup failed: 401 UNAUTHORIZED");
        });

        // When/Then
        assertThatThrownBy(() -> adapter.fetchTweets(username, null))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("Failed to fetch tweets");
    }
}
