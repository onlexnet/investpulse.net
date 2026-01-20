package net.investpulse.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;
import java.util.Set;

/**
 * Represents a raw Reddit post received from Reddit Search API.
 * Includes metadata for traceability and versioning support.
 */
public record RawRedditPost(
    String id,
    String title,
    String content,
    int upvotes,
    int comments,
    Instant timestamp,
    String subreddit,
    Set<String> tickers, // Extracted tickers like "AAPL", "TSLA"
    @JsonProperty("version") Integer version, // Version number for tracking changes
    @JsonProperty("lastUpdatedAt") Instant lastUpdatedAt // When this version was created
) {}
