package net.investpulse.reddit.infra.persistence.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.investpulse.common.dto.RawRedditPost;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

/**
 * Domain entity representing a Reddit post with versioning support.
 * Persisted via JDBC (no JPA/Hibernate annotations).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RedditPostEntity {

    private UUID id;
    private String postId;
    private String title;
    private String content;
    private Integer upvotes;
    private Integer comments;
    private String subreddit;
    private Instant createdAt;
    private Instant lastSeenAt;
    private Integer version;
    private Instant processedAt;

    /**
     * Creates a new entity from a RawRedditPost with specified version.
     */
    public static RedditPostEntity fromRawPost(RawRedditPost post, int version) {
        Instant now = Instant.now();
        return RedditPostEntity.builder()
                .postId(post.id())
                .title(post.title())
                .content(post.content())
                .upvotes(post.upvotes())
                .comments(post.comments())
                .subreddit(post.subreddit())
                .createdAt(post.timestamp())
                .lastSeenAt(now)
                .version(version)
                .processedAt(now)
                .build();
    }

    /**
     * Checks if this entity has changes compared to a RawRedditPost.
     */
    public boolean hasChanges(RawRedditPost post) {
        return !safeEquals(this.title, post.title())
                || !safeEquals(this.content, post.content())
                || !Objects.equals(this.upvotes, post.upvotes())
                || !Objects.equals(this.comments, post.comments());
    }

    private static boolean safeEquals(String a, String b) {
        if (a == null && b == null) return true;
        if (a == null || b == null) return false;
        return a.equals(b);
    }
}
