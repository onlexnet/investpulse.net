package net.investpulse.sentiment.converter;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.ScoredRedditPost;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Set;

/**
 * Converts {@link ScoredRedditPost} messages from Reddit Kafka topics into
 * a normalized {@link RawTweet} format for uniform processing by {@link SentimentAggregator}.
 * 
 * <p><strong>Normalization Strategy:</strong>
 * <ul>
 *   <li>Reddit post ID → tweetId field</li>
 *   <li>Subreddit name → publisher field (e.g., "r/stocks")</li>
 *   <li>Post timestamp (UTC) → preserved as-is in {@code createdAt} field</li>
 *   <li>Source field set to "reddit" for tracking data origin</li>
 *   <li>Tickers extracted from ticker field (single ticker from topic name)</li>
 * </ul>
 * 
 * <p><strong>Timezone Handling:</strong>
 * Original post timestamp is stored in UTC (epoch milliseconds). The local timezone
 * is configured for partition date calculation in Parquet files:
 * <ul>
 *   <li>If UTC+5:00, a post at 2026-01-07 23:00 UTC becomes 2026-01-08 04:00 local</li>
 *   <li>Parquet partition will use local date: 2026-01-08</li>
 *   <li>Original UTC timestamp preserved in {@code originalTimestamp} field for analytics</li>
 * </ul>
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RedditPostConverter {

    private static final String SOURCE_REDDIT = "reddit";
    private static final String REDDIT_PUBLISHER_PREFIX = "r/";

    @Value("${sentiment.timezone:UTC}")
    private String timezone;

    /**
     * Converts a scored Reddit post to a normalized RawTweet for sentiment analysis.
     * 
     * <p>The conversion creates a synthetic RawTweet with:
     * - Post ID as tweetId
     * - Subreddit name (with r/ prefix) as publisher
     * - Original post timestamp (UTC) for partition date calculation
     * - Source field set to "reddit"
     * - Single ticker extracted from the message
     * 
     * @param redditPost the scored Reddit post from Kafka
     * @return normalized RawTweet ready for sentiment analysis
     */
    public RawTweet convert(ScoredRedditPost redditPost) {
        log.debug("Converting Reddit post {} from r/{} to RawTweet format", 
            redditPost.id(), redditPost.subreddit());
        
        return new RawTweet(
            redditPost.id(),
            "", // Text field empty - Reddit body/title would require separate message enrichment
            "", // authorId - not available in ScoredRedditPost
            "", // authorUsername - not available in ScoredRedditPost
            redditPost.timestamp(),
            SOURCE_REDDIT,
            REDDIT_PUBLISHER_PREFIX + redditPost.subreddit(),
            Set.of(redditPost.ticker())
        );
    }

    /**
     * Extracts the local date from a UTC timestamp for Parquet partitioning.
     * 
     * <p>Converts UTC timestamp to local date using configured timezone.
     * This ensures that records are partitioned by the local date where they
     * occurred, not by UTC date.
     * 
     * <p>Example: A post at 2026-01-07 23:00 UTC in timezone UTC+5:00
     * becomes 2026-01-08 (local date) and is partitioned as day=08.
     * 
     * @param timestampUtc epoch milliseconds (UTC)
     * @return local date for partition calculation
     */
    public LocalDate getLocalPartitionDate(Instant timestampUtc) {
        var zoneId = ZoneId.of(timezone);
        return timestampUtc.atZone(zoneId).toLocalDate();
    }
}
