package net.investpulse.reddit.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.MessagePublisher;
import net.investpulse.reddit.domain.port.RedditPostFetcher;
import net.investpulse.reddit.infra.cache.PostDeduplicationCache;
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
    private final PostDeduplicationCache deduplicationCache;
    private final TickerExtractor tickerExtractor;
    private final RedditSentimentService sentimentService;

    @Value("${reddit.subreddits:stocks,investing,wallstreetbets}")
    private String subredditsConfig;

    // Metrics
    private volatile int totalPostsFetched = 0;
    private volatile int totalPostsPublished = 0;
    private volatile int totalDuplicates = 0;

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
        double totalWeightedScore = 0.0;

        for (String subreddit : subreddits) {
            try {
                List<RawRedditPost> posts = redditPostFetcher.fetchPostsByTicker(subreddit, ticker);
                fetchedCount += posts.size();

                for (RawRedditPost post : posts) {
                    if (deduplicationCache.isDuplicate(post.id())) {
                        totalDuplicates++;
                        log.debug("Skipping duplicate post {} from r/{}", post.id(), subreddit);
                        continue;
                    }

                    // Mark as processed
                    deduplicationCache.markAsProcessed(post.id());

                    // Analyze sentiment
                    String textForSentiment = post.title() + " " + (post.content() != null ? post.content() : "");
                    double rawScore = sentimentService.analyzeSentiment(textForSentiment);
                    double discretizedScore = sentimentService.discretizeSentiment(rawScore);
                    double weightedScore = sentimentService.calculateWeightedScore(
                            discretizedScore, post.upvotes(), post.comments()
                    );

                    totalWeightedScore += weightedScore;

                    // Publish raw post
                    messagePublisher.publishRawPost(post);

                    // Publish scored post
                    messagePublisher.publishScoredPost(
                            post.id(), ticker, discretizedScore, weightedScore,
                            post.upvotes(), post.comments()
                    );

                    publishedCount++;
                    log.debug("Published post {} from r/{}: sentiment={}, weighted={}", 
                            post.id(), subreddit, discretizedScore, weightedScore);
                }
            } catch (Exception e) {
                log.error("Error ingesting posts from r/{} for ticker {}", subreddit, ticker, e);
            }
        }

        // Update metrics
        totalPostsFetched += fetchedCount;
        totalPostsPublished += publishedCount;

        // Log summary
        double avgWeightedScore = publishedCount > 0 ? totalWeightedScore / publishedCount : 0.0;
        log.info("Ingestion complete for ticker {}: fetched={}, published={}, duplicates={}, " +
                        "avgWeightedSentiment={:.3f}, cacheSize={}",
                ticker, fetchedCount, publishedCount, totalDuplicates, avgWeightedScore,
                deduplicationCache.getSize());
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
                "totalDuplicates", totalDuplicates,
                "cacheSize", deduplicationCache.getSize()
        );
    }
}
