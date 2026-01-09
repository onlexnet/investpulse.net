package net.investpulse.common.dto;

import java.time.Instant;

/**
 * Represents a Reddit post with calculated sentiment score.
 * Used for downstream aggregation and analytics.
 * 
 * Note: Custom Instant deserialization is configured in sentiment-analyzer's
 * JacksonConfiguration to handle both milliseconds and seconds-format timestamps.
 */
public record ScoredRedditPost(
    String id,
    String ticker,
    double sentimentScore,     // -1.0 to +1.0
    double weightedScore,      // sentimentScore × log(1 + upvotes + comments)
    int upvotes,
    int comments,
    Instant timestamp,
    String subreddit
) {}
