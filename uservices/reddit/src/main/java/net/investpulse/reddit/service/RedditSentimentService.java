package net.investpulse.reddit.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Set;
import java.util.regex.Pattern;

/**
 * Service for analyzing sentiment of Reddit posts using financial lexicon.
 * Assigns discrete sentiment scores and calculates weighted scores.
 */
@Slf4j
@Service
public class RedditSentimentService {

    // Financial sentiment lexicon (simplified Loughran-McDonald)
    private static final Set<String> POSITIVE_WORDS = Set.of(
            "bullish", "upgrade", "profit", "growth", "beat", "success", "gains",
            "positive", "strong", "buy", "bull", "up", "surge", "rally", "boom",
            "excellent", "great", "love", "best", "outperform", "outperforming"
    );

    private static final Set<String> NEGATIVE_WORDS = Set.of(
            "bearish", "downgrade", "loss", "decline", "miss", "failure", "drop",
            "negative", "weak", "sell", "bear", "down", "crash", "plunge", "bust",
            "bad", "terrible", "hate", "worst", "underperform", "underperforming"
    );

    /**
     * Analyzes sentiment of text and returns a score between -1.0 and 1.0.
     *
     * @param text the text to analyze
     * @return sentiment score: -1.0 (very negative) to +1.0 (very positive)
     */
    public double analyzeSentiment(String text) {
        if (text == null || text.isEmpty()) {
            return 0.0; // neutral
        }

        String lowerText = text.toLowerCase();
        // Remove punctuation for word matching
        String cleanText = lowerText.replaceAll("[^a-z0-9\\s]", " ");
        String[] words = cleanText.split("\\s+");

        int positiveCount = 0;
        int negativeCount = 0;

        for (String word : words) {
            if (POSITIVE_WORDS.contains(word)) {
                positiveCount++;
            } else if (NEGATIVE_WORDS.contains(word)) {
                negativeCount++;
            }
        }

        // Calculate raw sentiment score
        int totalSentimentWords = positiveCount + negativeCount;
        if (totalSentimentWords == 0) {
            return 0.0; // neutral
        }

        double rawScore = (double) (positiveCount - negativeCount) / totalSentimentWords;
        // Clamp to [-1.0, 1.0]
        return Math.max(-1.0, Math.min(1.0, rawScore));
    }

    /**
     * Converts sentiment score to a discrete level.
     * Very Negative: -1.0, Negative: -0.5, Neutral: 0, Positive: 0.5, Very Positive: 1.0
     *
     * @param rawScore the raw sentiment score
     * @return discretized sentiment score
     */
    public double discretizeSentiment(double rawScore) {
        if (rawScore < -0.6) {
            return -1.0;  // Very negative
        } else if (rawScore < -0.2) {
            return -0.5;  // Negative
        } else if (rawScore <= 0.2) {
            return 0.0;   // Neutral
        } else if (rawScore <= 0.6) {
            return 0.5;   // Positive
        } else {
            return 1.0;   // Very positive
        }
    }

    /**
     * Calculates weighted sentiment score.
     * Formula: sentimentScore × log(1 + upvotes + comments)
     *
     * @param sentimentScore the discretized sentiment score
     * @param upvotes the number of upvotes
     * @param comments the number of comments
     * @return weighted sentiment score
     */
    public double calculateWeightedScore(double sentimentScore, int upvotes, int comments) {
        double engagement = 1.0 + upvotes + comments;
        double weight = Math.log(engagement);
        return sentimentScore * weight;
    }
}
