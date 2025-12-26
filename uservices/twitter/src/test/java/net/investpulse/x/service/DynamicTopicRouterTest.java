package net.investpulse.x.service;

import net.investpulse.common.dto.RawTweet;
import org.apache.kafka.clients.admin.NewTopic;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;

import java.time.Instant;
import java.util.Set;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DynamicTopicRouterTest {

    @Mock
    private KafkaTemplate<String, RawTweet> kafkaTemplate;

    @Mock
    private KafkaAdmin kafkaAdmin;

    @InjectMocks
    private DynamicTopicRouter router;

    @Test
    void shouldRouteToMultipleTopics() {
        RawTweet tweet = new RawTweet(
            "1", "Test $AAPL and $TSLA", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL", "TSLA")
        );

        router.route(tweet);

        verify(kafkaAdmin, times(2)).createOrModifyTopics(any());
        
        verify(kafkaTemplate).send(eq("ticker-AAPL"), eq("AAPL"), eq(tweet));
        verify(kafkaTemplate).send(eq("ticker-TSLA"), eq("TSLA"), eq(tweet));
    }

    @Test
    void shouldNotRouteIfNoTickers() {
        RawTweet tweet = new RawTweet(
            "1", "No tickers here", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of()
        );

        router.route(tweet);

        verifyNoInteractions(kafkaAdmin);
        verifyNoInteractions(kafkaTemplate);
    }

    @Test
    void shouldNotRecreateExistingTopic() {
        RawTweet tweet = new RawTweet(
            "1", "$AAPL", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL")
        );

        router.route(tweet);
        router.route(tweet);

        // Should only call createOrModifyTopics once for AAPL
        verify(kafkaAdmin, times(1)).createOrModifyTopics(any());
        verify(kafkaTemplate, times(2)).send(eq("ticker-AAPL"), eq("AAPL"), eq(tweet));
    }
}
