package net.investpulse.reddit.infra.persistence.entity;

import jakarta.persistence.*;
import lombok.*;
import net.investpulse.common.dto.RawRedditPost;

import java.time.Instant;
import java.util.UUID;

/**
 * JPA entity representing a Reddit post with versioning support.
 * Each change to a post (upvotes, comments, title, content) creates a new version.
 */
@Entity
@Table(name = "reddit_posts", uniqueConstraints = {
    @UniqueConstraint(name = "uk_post_id", columnNames = "post_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RedditPostEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "post_id", nullable = false, length = 50)
    private String postId;

    @Column(name = "title", columnDefinition = "TEXT")
    private String title;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Column(name = "upvotes", nullable = false)
    private Integer upvotes;

    @Column(name = "comments", nullable = false)
    private Integer comments;

    @Column(name = "subreddit", nullable = false, length = 50)
    private String subreddit;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "last_seen_at", nullable = false)
    private Instant lastSeenAt;

    @Column(name = "version", nullable = false)
    private Integer version;

    @Column(name = "processed_at", nullable = false)
    private Instant processedAt;

    /**
     * Creates a new entity from a RawRedditPost with specified version.
     */
    public static RedditPostEntity fromRawPost(RawRedditPost post, int version) {
        return RedditPostEntity.builder()
                .postId(post.id())
                .title(post.title())
                .content(post.content())
                .upvotes(post.upvotes())
                .comments(post.comments())
                .subreddit(post.subreddit())
                .createdAt(post.timestamp())
                .lastSeenAt(Instant.now())
                .version(version)
                .processedAt(Instant.now())
                .build();
    }

    /**
     * Checks if this entity has changes compared to a RawRedditPost.
     */
    public boolean hasChanges(RawRedditPost post) {
        return !this.title.equals(post.title())
                || !safeEquals(this.content, post.content())
                || !this.upvotes.equals(post.upvotes())
                || !this.comments.equals(post.comments());
    }

    private static boolean safeEquals(String a, String b) {
        if (a == null && b == null) return true;
        if (a == null || b == null) return false;
        return a.equals(b);
    }
}
