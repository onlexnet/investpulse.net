package net.investpulse.reddit.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostRepository;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
        var maybeOpt = repository.findLatestVersion(post.id());

        if (maybeOpt.isEmpty()) {
            RedditPostEntity saved = repository.saveNew(post);
            log.debug("New post saved: postId={}, version={}", post.id(), saved.getVersion());
            return new DeduplicationResult(PostStatus.NEW, saved.getVersion());
        }

        RedditPostEntity existing = maybeOpt.get();

        // Check if post has changes
        if (existing.hasChanges(post)) {
            RedditPostEntity updated = repository.saveUpdated(existing, post);
            log.debug("Post updated: postId={}, version={} -> {}", post.id(), existing.getVersion(), updated.getVersion());
            return new DeduplicationResult(PostStatus.UPDATED, updated.getVersion());
        }

        // No changes - update last_seen_at timestamp only
        RedditPostEntity touched = repository.touchLastSeen(existing);
        log.debug("Post unchanged: postId={}, version={}", post.id(), touched.getVersion());
        return new DeduplicationResult(PostStatus.UNCHANGED, touched.getVersion());
    }
}
