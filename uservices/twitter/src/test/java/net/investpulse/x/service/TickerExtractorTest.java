package net.investpulse.x.service;

import org.junit.jupiter.api.Test;
import java.util.Set;
import static org.junit.jupiter.api.Assertions.*;

class TickerExtractorTest {

    private final TickerExtractor extractor = new TickerExtractor();

    @Test
    void shouldExtractTickersWithDollarSign() {
        String text = "Watching $AAPL and $TSLA closely today!";
        Set<String> result = extractor.extract(text);
        
        assertEquals(2, result.size());
        assertTrue(result.contains("AAPL"));
        assertTrue(result.contains("TSLA"));
    }

    @Test
    void shouldExtractTickersWithHashtag() {
        String text = "Market update #NVDA #AMD";
        Set<String> result = extractor.extract(text);
        
        assertEquals(2, result.size());
        assertTrue(result.contains("NVDA"));
        assertTrue(result.contains("AMD"));
    }

    @Test
    void shouldHandleMixedFormats() {
        String text = "Long $MSFT and #GOOGL";
        Set<String> result = extractor.extract(text);
        
        assertEquals(2, result.size());
        assertTrue(result.contains("MSFT"));
        assertTrue(result.contains("GOOGL"));
    }

    @Test
    void shouldIgnoreInvalidTickers() {
        String text = "This is just a $ sign and a # tag without letters";
        Set<String> result = extractor.extract(text);
        assertTrue(result.isEmpty());
    }

    @Test
    void shouldHandleNullAndEmpty() {
        assertTrue(extractor.extract(null).isEmpty());
        assertTrue(extractor.extract("").isEmpty());
    }

    @Test
    void shouldHandleCaseInsensitivity() {
        String text = "Watching $aapl";
        Set<String> result = extractor.extract(text);
        assertEquals(1, result.size());
        assertTrue(result.contains("AAPL"));
    }
}
