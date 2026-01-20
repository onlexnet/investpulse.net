package net.investpulse.reddit.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.MessagePublisher;
import net.investpulse.reddit.domain.port.RedditPostFetcher;
import net.investpulse.reddit.service.DatabaseDeduplicationService.DeduplicationResult;
import net.investpulse.reddit.service.DatabaseDeduplicationService.PostStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Core ingestor service that orchestrates Reddit post fetching, deduplication,
 * sentiment analysis, and publication.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RedditIngestor {

    private final RedditPostFetcher redditPostFetcher;
    private final MessagePublisher messagePublisher;
    private final DatabaseDeduplicationService deduplicationService;
    private final TickerExtractor tickerExtractor;
    private final RedditSentimentService sentimentService;

    @Value("${reddit.subreddits:stocks,investing,wallstreetbets}")
    private String subredditsConfig;

    // Metrics
    private volatile int totalPostsFetched = 0;
    private volatile int totalPostsPublished = 0;
    private volatile int totalUnchanged = 0;
    private volatile int totalUpdates = 0;

    /**
     * Ingests posts from all configured subreddits for a given ticker.
     * Handles deduplication, scoring, and publication.
     *
     * @param ticker the stock ticker to search for (e.g., "AAPL")
     */
    public void ingestPostsForTicker(String ticker) {
        List<String> subreddits = parseSubreddits();
        log.info("Starting ingestion for ticker {} from {} subreddit(s)", ticker, subreddits.size());

        int fetchedCount = 0;
        int publishedCount = 0;
        int unchangedCount = 0;
        int updatedCount = 0;
        double totalWeightedScore = 0.0;

        for (String subreddit : subreddits) {
            try {
                List<RawRedditPost> posts = redditPostFetcher.fetchPostsByTicker(subreddit, ticker);
                fetchedCount += posts.size();

                for (RawRedditPost post : posts) {
                    // Check post against database
                    DeduplicationResult result = deduplicationService.checkAndSavePost(post);

                    if (result.status() == PostStatus.UNCHANGED) {
                        unchangedCount++;
                        log.debug("Skipping unchanged post {} from r/{}, version={}", 
                                post.id(), subreddit, result.version());
                        continue;
                    }

                    if (result.status() == PostStatus.UPDATED) {
                        updatedCount++;
                    }

                    // Analyze sentiment
                    String textForSentiment = post.title() + " " + (post.content() != null ? post.content() : "");
                    double rawScore = sentimentService.analyzeSentiment(textForSentiment);
                    double discretizedScore = sentimentService.discretizeSentiment(rawScore);
                    double weightedScore = sentimentService.calculateWeightedScore(
                            discretizedScore, post.upvotes(), post.comments()
                    );

                    totalWeightedScore += weightedScore;

                    // Publish raw post with version
                    messagePublisher.publishRawPost(post, result.version());

                    // Publish scored post with version
                    messagePublisher.publishScoredPost(
                            post.id(), ticker, discretizedScore, weightedScore,
                            post.upvotes(), post.comments(), post.timestamp(), result.version()
                    );

                    publishedCount++;
                    log.debug("Published post {} from r/{}: sentiment={}, weighted={}, version={}, status={}", 
                            post.id(), subreddit, discretizedScore, weightedScore, result.version(), result.status());
                }
            } catch (Exception e) {
                log.error("Error ingesting posts from r/{} for ticker {}", subreddit, ticker, e);
            }
        }

        // Update metrics
        totalPostsFetched += fetchedCount;
        totalPostsPublished += publishedCount;
        totalUnchanged += unchangedCount;
        totalUpdates += updatedCount;

        // Log summary
        double avgWeightedScore = publishedCount > 0 ? totalWeightedScore / publishedCount : 0.0;
        log.info("Ingestion complete for ticker {}: fetched={}, published={}, unchanged={}, updates={}, " +
                        "avgWeightedSentiment={:.3f}",
                ticker, fetchedCount, publishedCount, unchangedCount, updatedCount, avgWeightedScore);
    }

    /**
     * Parses the configured subreddit list.
     */
    private List<String> parseSubreddits() {
        return Arrays.stream(subredditsConfig.split(","))
                .map(String::trim)
                .toList();
    }

    /**
     * Returns ingestion metrics.
     */
    public Map<String, Object> getMetrics() {
        return Map.of(
                "totalPostsFetched", totalPostsFetched,
                "totalPostsPublished", totalPostsPublished,
                "totalUnchanged", totalUnchanged,
                "totalUpdates", totalUpdates
        );
    }
}
