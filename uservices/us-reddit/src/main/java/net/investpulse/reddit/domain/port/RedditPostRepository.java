package net.investpulse.reddit.domain.port;

import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;

import java.util.Optional;

/**
 * Port interface for Reddit post persistence operations.
 * Follows hexagonal architecture pattern.
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
     * Saves a Reddit post entity.
     *
     * @param entity the entity to save
     * @return the saved entity
     */
    RedditPostEntity save(RedditPostEntity entity);
}
