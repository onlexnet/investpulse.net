package net.investpulse.reddit.infra.persistence;

import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Spring Data JPA repository for Reddit posts.
 */
@Repository
public interface JpaRedditPostRepository extends JpaRepository<RedditPostEntity, UUID> {

    /**
     * Finds the latest version of a post by post ID.
     * Uses the indexed (post_id, version DESC) for efficient lookup.
     */
    @Query("SELECT r FROM RedditPostEntity r WHERE r.postId = :postId ORDER BY r.version DESC LIMIT 1")
    Optional<RedditPostEntity> findLatestByPostId(@Param("postId") String postId);
}
