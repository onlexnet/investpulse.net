package net.investpulse.sentiment.service;

import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Set;

@Service
public class FinancialSentimentService {

    // Simplified Loughran-McDonald / Financial Lexicon
    private static final Set<String> POSITIVE = Set.of(
        "BULLISH", "UPGRADE", "PROFIT", "GROWTH", "BEAT", "SUCCESS", "GAINS", "POSITIVE", "STRONG", "BUY"
    );

    private static final Set<String> NEGATIVE = Set.of(
        "BEARISH", "DOWNGRADE", "LOSS", "DECLINE", "MISS", "FAILURE", "DROP", "NEGATIVE", "WEAK", "SELL"
    );

    public double analyze(String text) {
        if (text == null || text.isEmpty()) return 0.0;

        String[] words = text.toUpperCase().split("\\s+");
        int score = 0;
        int count = 0;

        for (String word : words) {
            // Clean word from punctuation
            String cleanWord = word.replaceAll("[^A-Z]", "");
            if (POSITIVE.contains(cleanWord)) {
                score++;
                count++;
            } else if (NEGATIVE.contains(cleanWord)) {
                score--;
                count++;
            }
        }

        if (count == 0) return 0.0;
        return (double) score / count;
    }

    public String getSentimentLabel(double score) {
        if (score > 0.05) return "POSITIVE";
        if (score < -0.05) return "NEGATIVE";
        return "NEUTRAL";
    }
}
