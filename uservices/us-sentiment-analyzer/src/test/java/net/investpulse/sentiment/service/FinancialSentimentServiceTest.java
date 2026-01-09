package net.investpulse.sentiment.service;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FinancialSentimentServiceTest {

    private final FinancialSentimentService service = new FinancialSentimentService();

    @Test
    void shouldReturnPositiveScoreForBullishText() {
        var text = "Strong growth and profit beat expectations. Bullish on this stock!";
        var score = service.analyze(text);
        assertTrue(score > 0);
        assertEquals("POSITIVE", service.getSentimentLabel(score));
    }

    @Test
    void shouldReturnNegativeScoreForBearishText() {
        var text = "Major loss and decline in revenue. Missed targets. Sell now.";
        var score = service.analyze(text);
        assertTrue(score < 0);
        assertEquals("NEGATIVE", service.getSentimentLabel(score));
    }

    @Test
    void shouldReturnNeutralScoreForMixedText() {
        var text = "The company had some growth but also some loss.";
        var score = service.analyze(text);
        assertEquals(0.0, score);
        assertEquals("NEUTRAL", service.getSentimentLabel(score));
    }

    @Test
    void shouldHandleNullAndEmpty() {
        assertEquals(0.0, service.analyze(null));
        assertEquals(0.0, service.analyze(""));
        assertEquals("NEUTRAL", service.getSentimentLabel(0.0));
    }

    @Test
    void shouldIgnoreNonFinancialWords() {
        var text = "The weather is nice today in New York.";
        assertEquals(0.0, service.analyze(text));
    }
}
