package net.investpulse.x.service;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.config.TwitterConfig;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;
import java.util.Set;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TwitterIngestorTest {

    @Mock
    private TwitterConfig config;

    @Mock
    private TickerExtractor tickerExtractor;

    @Mock
    private DynamicTopicRouter topicRouter;

    @InjectMocks
    @Spy
    private TwitterIngestor ingestor;

    @Test
    void shouldPollAndRouteTweets() {
        when(config.getAccountsToFollow()).thenReturn(List.of("ZeroHedge"));
        
        RawTweet tweet = new RawTweet(
            "100", "Test", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL")
        );
        
        doReturn(List.of(tweet)).when(ingestor).fetchTweetsForAccount(eq("ZeroHedge"), any());

        ingestor.pollTweets();

        verify(topicRouter).route(tweet);
    }

    @Test
    void shouldHandleExceptionDuringPoll() {
        when(config.getAccountsToFollow()).thenReturn(List.of("ZeroHedge"));
        doThrow(new RuntimeException("API Error")).when(ingestor).fetchTweetsForAccount(anyString(), any());

        // Should not throw exception
        ingestor.pollTweets();

        verifyNoInteractions(topicRouter);
    }
}
