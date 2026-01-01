package net.investpulse.x.service;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.config.TwitterConfig;
import net.investpulse.x.config.TwitterProps;
import net.investpulse.x.domain.port.TweetFetcher;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
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
    private TwitterProps.Configuration config;

    @Mock
    private TweetFetcher tweetFetcher;

    @Mock
    private TickerExtractor tickerExtractor;

    @Mock
    private DynamicTopicRouter topicRouter;

    @InjectMocks
    private TwitterIngestor ingestor;

    @Test
    void shouldPollAndRouteTweets() {
        when(config.accountsToFollow()).thenReturn(List.of("ZeroHedge"));
        
        RawTweet tweet = new RawTweet(
            "100", "Test", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL")
        );
        
        when(tweetFetcher.fetchTweets(eq("ZeroHedge"), any())).thenReturn(List.of(tweet));

        ingestor.pollTweets();

        verify(topicRouter).route(tweet);
    }

    @Test
    void shouldHandleExceptionDuringPoll() {
        when(config.accountsToFollow()).thenReturn(List.of("ZeroHedge"));
        when(tweetFetcher.fetchTweets(anyString(), any())).thenThrow(new RuntimeException("API Error"));

        // Should not throw exception
        ingestor.pollTweets();

        verifyNoInteractions(topicRouter);
    }
}

