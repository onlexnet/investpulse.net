package net.investpulse.x.service;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.MessagePublisher;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Set;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DynamicTopicRouterTest {

    @Mock
    private MessagePublisher messagePublisher;

    @InjectMocks
    private DynamicTopicRouter router;

    @Test
    void shouldRouteToMultipleTopics() {
        RawTweet tweet = new RawTweet(
            "1", "Test $AAPL and $TSLA", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL", "TSLA")
        );

        router.route(tweet);

        verify(messagePublisher).ensureTopicExists("ticker-AAPL");
        verify(messagePublisher).ensureTopicExists("ticker-TSLA");
        
        verify(messagePublisher).publish(eq("ticker-AAPL"), eq("AAPL"), eq(tweet));
        verify(messagePublisher).publish(eq("ticker-TSLA"), eq("TSLA"), eq(tweet));
    }

    @Test
    void shouldNotRouteIfNoTickers() {
        RawTweet tweet = new RawTweet(
            "1", "No tickers here", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of()
        );

        router.route(tweet);

        verifyNoInteractions(messagePublisher);
    }

    @Test
    void shouldNotRecreateExistingTopic() {
        RawTweet tweet = new RawTweet(
            "1", "$AAPL", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL")
        );

        router.route(tweet);
        router.route(tweet);

        // Should only call ensureTopicExists once for AAPL
        verify(messagePublisher, times(1)).ensureTopicExists("ticker-AAPL");
        verify(messagePublisher, times(2)).publish(eq("ticker-AAPL"), eq("AAPL"), eq(tweet));
    }
}
