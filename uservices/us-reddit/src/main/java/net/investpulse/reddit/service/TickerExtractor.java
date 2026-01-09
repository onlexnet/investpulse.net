package net.investpulse.reddit.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Service for extracting stock ticker symbols from text.
 * Uses regex pattern matching with word boundaries.
 */
@Slf4j
@Service
public class TickerExtractor {

    // Pattern: matches $AAPL or #TSLA or standalone AAPL (1-5 uppercase letters with word boundaries)
    private static final Pattern TICKER_PATTERN = Pattern.compile("[$#]?([A-Z]{1,5})\\b");

    /**
     * Extracts unique ticker symbols from text.
     *
     * @param text the text to search for tickers
     * @return set of extracted tickers (uppercase)
     */
    public Set<String> extractTickers(String text) {
        if (text == null || text.isEmpty()) {
            return Set.of();
        }

        Set<String> tickers = new HashSet<>();
        Matcher matcher = TICKER_PATTERN.matcher(text);

        while (matcher.find()) {
            String ticker = matcher.group(1);
            // Basic filter: exclude common words that might match (e.g., "AND", "THE")
            if (!isCommonWord(ticker)) {
                tickers.add(ticker);
            }
        }

        return tickers;
    }

    /**
     * Filters out common English words that match the ticker pattern.
     */
    private boolean isCommonWord(String ticker) {
        // List of common words to exclude
        Set<String> commonWords = Set.of(
                "AND", "THE", "ARE", "FOR", "NOT", "BUT", "CAN", "HAD", "HAS", "HER",
                "HIS", "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "ONE", "OUR", "OUT",
                "OWN", "SAY", "SHE", "TOO", "USE", "WAS", "WAY", "WHO", "WHY", "YET",
                "BIG", "DAY", "DID", "GET", "GOT", "HER", "HIM", "HIS", "HOW", "LOT",
                "MEN", "NET", "TRY", "TWO", "BAD", "BIT", "END", "FAR", "FEW", "GOD",
                "HOT", "MAN", "OFF", "PUT", "RUN", "SET", "SIT", "TOP", "WIN", "YES"
        );
        return commonWords.contains(ticker);
    }
}
