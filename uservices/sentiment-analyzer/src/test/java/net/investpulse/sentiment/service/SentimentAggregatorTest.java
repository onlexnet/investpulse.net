package net.investpulse.sentiment.service;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.SentimentResult;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.core.KafkaTemplate;

import java.time.Instant;
import java.util.Set;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SentimentAggregatorTest {

    @Mock
    private FinancialSentimentService sentimentService;

    @Mock
    private KafkaTemplate<String, SentimentResult> kafkaTemplate;

    @InjectMocks
    private SentimentAggregator aggregator;

    @Test
    void shouldProcessTweetAndPublishResult() {
        RawTweet tweet = new RawTweet(
            "1", "Bullish on $AAPL", "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of("AAPL")
        );
        String topic = "ticker-AAPL";

        when(sentimentService.analyze(anyString())).thenReturn(0.8);
        when(sentimentService.getSentimentLabel(0.8)).thenReturn("POSITIVE");

        aggregator.processTweet(tweet, topic);

        verify(sentimentService).analyze(tweet.text());
        verify(kafkaTemplate).send(eq("sentiment-aggregated"), eq("AAPL"), any(SentimentResult.class));
    }
}
