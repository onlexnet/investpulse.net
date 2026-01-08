package net.investpulse.common.dto;

import java.time.Instant;
import java.util.Set;

/**
 * Represents a raw Reddit post received from Reddit Search API.
 * Includes metadata for traceability.
 */
public record RawRedditPost(
    String id,
    String title,
    String content,
    int upvotes,
    int comments,
    Instant timestamp,
    String subreddit,
    Set<String> tickers // Extracted tickers like "AAPL", "TSLA"
) {}
