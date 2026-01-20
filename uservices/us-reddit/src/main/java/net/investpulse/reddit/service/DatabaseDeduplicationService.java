package net.investpulse.reddit.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostRepository;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Optional;

/**
 * Service for database-backed deduplication and versioning of Reddit posts.
 * Replaces the previous in-memory Caffeine cache with persistent PostgreSQL storage.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DatabaseDeduplicationService {

    private final RedditPostRepository repository;

    /**
     * Status of a post after deduplication check.
     */
    public enum PostStatus {
        /** Post has never been seen before */
        NEW,
        /** Post exists but has no changes */
        UNCHANGED,
        /** Post exists and has changes (title, content, upvotes, or comments) */
        UPDATED
    }

    /**
     * Result of a deduplication check.
     */
    public record DeduplicationResult(PostStatus status, int version) {}

    /**
     * Checks a post against the database for deduplication and change detection.
     * Saves the post to database and returns its status and version number.
     *
     * @param post the raw Reddit post to check
     * @return the deduplication result with status and version
     */
    @Transactional
    public DeduplicationResult checkAndSavePost(RawRedditPost post) {
        Optional<RedditPostEntity> existingOpt = repository.findLatestVersion(post.id());

        if (existingOpt.isEmpty()) {
            // New post - save as version 1
            RedditPostEntity newEntity = RedditPostEntity.fromRawPost(post, 1);
            repository.save(newEntity);
            log.debug("New post saved: postId={}, version=1", post.id());
            return new DeduplicationResult(PostStatus.NEW, 1);
        }

        RedditPostEntity existing = existingOpt.get();

        // Check if post has changes
        if (existing.hasChanges(post)) {
            // Post updated - increment version
            int newVersion = existing.getVersion() + 1;
            RedditPostEntity updatedEntity = RedditPostEntity.fromRawPost(post, newVersion);
            repository.save(updatedEntity);
            log.debug("Post updated: postId={}, version={} -> {}", post.id(), existing.getVersion(), newVersion);
            return new DeduplicationResult(PostStatus.UPDATED, newVersion);
        }

        // No changes - update last_seen_at timestamp only
        existing.setLastSeenAt(Instant.now());
        repository.save(existing);
        log.debug("Post unchanged: postId={}, version={}", post.id(), existing.getVersion());
        return new DeduplicationResult(PostStatus.UNCHANGED, existing.getVersion());
    }
}
