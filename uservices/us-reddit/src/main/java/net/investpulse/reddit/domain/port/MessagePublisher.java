package net.investpulse.reddit.domain.port;

import net.investpulse.common.dto.RawRedditPost;

/**
 * Port interface for publishing Reddit posts to Kafka topics.
 * Abstracts message publishing infrastructure from business logic.
 */
public interface MessagePublisher {

    /**
     * Publishes a raw Reddit post to the reddit-raw topic.
     *
     * @param post the raw Reddit post to publish
     * @param version the version number of this post
     */
    void publishRawPost(RawRedditPost post, int version);

    /**
     * Publishes a scored Reddit post to the reddit-scored topic.
     *
     * @param postId the post ID (unique identifier)
     * @param ticker the stock ticker symbol
     * @param sentimentScore the sentiment score (-1.0 to +1.0)
     * @param weightedScore the weighted sentiment score (score × log(1 + upvotes + comments))
     * @param upvotes the number of upvotes
     * @param comments the number of comments
     * @param timestamp the original timestamp of the post from Reddit API
     * @param version the version number of this post
     */
    void publishScoredPost(String postId, String ticker, double sentimentScore, 
                          double weightedScore, int upvotes, int comments, 
                          java.time.Instant timestamp, int version);
}
