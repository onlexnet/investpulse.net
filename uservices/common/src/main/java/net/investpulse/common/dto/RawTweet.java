package net.investpulse.common.dto;

import java.time.Instant;
import java.util.Set;

/**
 * Represents a raw tweet received from X (Twitter) API.
 * Includes metadata for traceability.
 */
public record RawTweet(
    String id,
    String text,
    String authorId,
    String authorUsername,
    Instant createdAt,
    String source, // e.g., "X API"
    String publisher, // e.g., "@ZeroHedge"
    Set<String> tickers // Extracted tickers like "AAPL", "TSLA"
) {}
