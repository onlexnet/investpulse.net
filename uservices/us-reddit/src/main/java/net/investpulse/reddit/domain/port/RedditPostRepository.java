package net.investpulse.reddit.domain.port;

import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;

import java.util.Optional;

/**
 * Port interface for Reddit post persistence operations (JDBC-backed).
 */
public interface RedditPostRepository {

    /**
     * Finds the latest version of a Reddit post by post ID.
     *
     * @param postId the Reddit post ID
     * @return the latest version of the post, or empty if not found
     */
    Optional<RedditPostEntity> findLatestVersion(String postId);

    /**
     * Inserts a new Reddit post (version 1).
     */
    RedditPostEntity saveNew(RawRedditPost post);

    /**
     * Persists an updated Reddit post, incrementing the version in the database.
     */
    RedditPostEntity saveUpdated(RedditPostEntity existing, RawRedditPost post);

    /**
     * Updates only the lastSeenAt timestamp for an unchanged post.
     */
    RedditPostEntity touchLastSeen(RedditPostEntity existing);
}
