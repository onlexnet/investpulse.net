package net.investpulse.x.service;

import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class TickerExtractor {
    // Matches $TICKER or #TICKER (e.g., $AAPL, #TSLA)
    private static final Pattern TICKER_PATTERN = Pattern.compile("[$#]([A-Z]{1,5})\\b");

    public Set<String> extract(String text) {
        Set<String> tickers = new HashSet<>();
        if (text == null) return tickers;

        Matcher matcher = TICKER_PATTERN.matcher(text.toUpperCase());
        while (matcher.find()) {
            tickers.add(matcher.group(1));
        }
        return tickers;
    }
}
