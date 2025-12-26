package net.investpulse.common.dto;

import java.time.Instant;

/**
 * Represents the result of sentiment analysis for a specific ticker.
 */
public record SentimentResult(
    String tweetId,
    String ticker,
    double score, // e.g., -1.0 to 1.0
    String sentiment, // e.g., "POSITIVE", "NEGATIVE", "NEUTRAL"
    Instant processedAt,
    String publisher,
    String source
) {}
