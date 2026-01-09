package net.investpulse.common.dto;

import java.time.Instant;

/**
 * Represents the result of sentiment analysis for a specific ticker.
 * 
 * <p><strong>Timestamp Fields:</strong>
 * <ul>
 *   <li>{@code originalTimestamp}: The original creation time from source (Twitter/Reddit), in UTC epoch milliseconds</li>
 *   <li>{@code processedAt}: The time this sentiment analysis was performed</li>
 * </ul>
 * 
 * <p>The {@code originalTimestamp} is preserved for accurate date-based partitioning
 * in Parquet files using local timezone conversion, while {@code processedAt}
 * tracks when the message was processed by the sentiment analyzer.
 */
public record SentimentResult(
    String tweetId,
    String ticker,
    double score, // e.g., -1.0 to 1.0
    String sentiment, // e.g., "POSITIVE", "NEGATIVE", "NEUTRAL"
    Instant processedAt,
    String publisher,
    String source, // e.g., "twitter" or "reddit"
    Instant originalTimestamp // Original creation time from source (Twitter/Reddit) in UTC
) {}
