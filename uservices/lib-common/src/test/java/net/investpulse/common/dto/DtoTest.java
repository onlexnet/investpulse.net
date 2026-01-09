package net.investpulse.common.dto;

import org.junit.jupiter.api.Test;
import java.time.Instant;
import java.util.Set;
import static org.junit.jupiter.api.Assertions.*;

class DtoTest {

    @Test
    void testRawTweet() {
        Instant now = Instant.now();
        RawTweet tweet = new RawTweet("1", "text", "auth1", "user1", now, "src", "pub", Set.of("AAPL"));
        
        assertEquals("1", tweet.id());
        assertEquals("text", tweet.text());
        assertEquals(now, tweet.createdAt());
        assertTrue(tweet.tickers().contains("AAPL"));
    }

    @Test
    void testSentimentResult() {
        Instant now = Instant.now();
        SentimentResult result = new SentimentResult("1", "AAPL", 0.5, "POSITIVE", now, "pub", "src", now);
        
        assertEquals("1", result.tweetId());
        assertEquals("AAPL", result.ticker());
        assertEquals(0.5, result.score());
        assertEquals("POSITIVE", result.sentiment());
        assertEquals(now, result.originalTimestamp());
    }
}
