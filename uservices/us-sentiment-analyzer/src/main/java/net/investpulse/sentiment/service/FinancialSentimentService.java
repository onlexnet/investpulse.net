package net.investpulse.sentiment.service;

import com.google.common.base.Splitter;
import org.springframework.stereotype.Service;

import java.util.Set;

@Service
public class FinancialSentimentService {

    private static final double NEUTRAL_SCORE = 0.0;
    private static final double POSITIVE_THRESHOLD = 0.05;
    private static final double NEGATIVE_THRESHOLD = -0.05;
    private static final String WORD_SEPARATOR_PATTERN = "\\s+";
    private static final String NON_ALPHA_PATTERN = "[^A-Z]";
    private static final String EMPTY_STRING = "";
    private static final Splitter WORD_SPLITTER = Splitter.onPattern(WORD_SEPARATOR_PATTERN).omitEmptyStrings();
    
    private static final String SENTIMENT_POSITIVE = "POSITIVE";
    private static final String SENTIMENT_NEGATIVE = "NEGATIVE";
    private static final String SENTIMENT_NEUTRAL = "NEUTRAL";

    // Simplified Loughran-McDonald / Financial Lexicon
    private static final Set<String> POSITIVE = Set.of(
        "BULLISH", "UPGRADE", "PROFIT", "GROWTH", "BEAT", "SUCCESS", "GAINS", "POSITIVE", "STRONG", "BUY"
    );

    private static final Set<String> NEGATIVE = Set.of(
        "BEARISH", "DOWNGRADE", "LOSS", "DECLINE", "MISS", "FAILURE", "DROP", "NEGATIVE", "WEAK", "SELL"
    );

    public double analyze(String text) {
        if (text == null || text.isEmpty()) {
            return NEUTRAL_SCORE;
        }

        var words = WORD_SPLITTER.split(text.toUpperCase());
        var score = 0;
        var count = 0;

        for (var word : words) {
            // Clean word from punctuation
            var cleanWord = word.replaceAll(NON_ALPHA_PATTERN, EMPTY_STRING);
            if (POSITIVE.contains(cleanWord)) {
                score++;
                count++;
            } else if (NEGATIVE.contains(cleanWord)) {
                score--;
                count++;
            }
        }

        if (count == 0) {
            return NEUTRAL_SCORE;
        }
        return (double) score / count;
    }

    public String getSentimentLabel(double score) {
        if (score > POSITIVE_THRESHOLD) {
            return SENTIMENT_POSITIVE;
        }
        if (score < NEGATIVE_THRESHOLD) {
            return SENTIMENT_NEGATIVE;
        }
        return SENTIMENT_NEUTRAL;
    }
}
