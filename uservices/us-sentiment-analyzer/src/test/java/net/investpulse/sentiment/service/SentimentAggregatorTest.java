package net.investpulse.sentiment.service;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.SentimentResult;
import net.investpulse.sentiment.persistence.ParquetSentimentWriter;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.Acknowledgment;

import java.time.Instant;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SentimentAggregatorTest {

    private static final double SAMPLE_POSITIVE_SCORE = 0.8;
    private static final String SAMPLE_TICKER = "AAPL";
    private static final String SAMPLE_TOPIC = "ticker-AAPL";
    private static final String SAMPLE_TWEET_TEXT = "Bullish on $AAPL";
    private static final String SENTIMENT_POSITIVE = "POSITIVE";

    @Mock
    private FinancialSentimentService sentimentService;

    @Mock
    private KafkaTemplate<String, SentimentResult> kafkaTemplate;

    @Mock
    private ParquetSentimentWriter parquetWriter;

    @Mock
    private Acknowledgment acknowledgment;

    @InjectMocks
    private SentimentAggregator aggregator;

    @Test
    void shouldProcessTweetAndPublishResultWithParquetPersistence() {
        var tweet = new RawTweet(
            "1", SAMPLE_TWEET_TEXT, "user1", "user1", 
            Instant.now(), "X API", "@ZeroHedge", Set.of(SAMPLE_TICKER)
        );

        when(sentimentService.analyze(anyString())).thenReturn(SAMPLE_POSITIVE_SCORE);
        when(sentimentService.getSentimentLabel(SAMPLE_POSITIVE_SCORE)).thenReturn(SENTIMENT_POSITIVE);
        when(parquetWriter.writeAsync(any(SentimentResult.class)))
            .thenReturn(CompletableFuture.completedFuture(null));

        aggregator.processTweet(tweet, SAMPLE_TOPIC, acknowledgment);

        verify(sentimentService).analyze(tweet.text());
        verify(kafkaTemplate).send(eq("sentiment-aggregated"), eq(SAMPLE_TICKER), any(SentimentResult.class));
        verify(parquetWriter).writeAsync(any(SentimentResult.class));
        verify(acknowledgment).acknowledge();
    }

    @Test
    void shouldNotAcknowledgeWhenParquetWriteFails() {
        var tweet = new RawTweet(
            "2", SAMPLE_TWEET_TEXT, "user1", "user1",
            Instant.now(), "X API", "@ZeroHedge", Set.of(SAMPLE_TICKER)
        );

        when(sentimentService.analyze(anyString())).thenReturn(SAMPLE_POSITIVE_SCORE);
        when(sentimentService.getSentimentLabel(SAMPLE_POSITIVE_SCORE)).thenReturn(SENTIMENT_POSITIVE);
        when(parquetWriter.writeAsync(any(SentimentResult.class)))
            .thenReturn(CompletableFuture.failedFuture(new RuntimeException("Disk full")));

        aggregator.processTweet(tweet, SAMPLE_TOPIC, acknowledgment);

        verify(parquetWriter).writeAsync(any(SentimentResult.class));
        verify(acknowledgment, never()).acknowledge();
    }
}
