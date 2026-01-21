package net.investpulse.reddit.infra.persistence;

import lombok.RequiredArgsConstructor;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import jakarta.annotation.Nullable;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
@RequiredArgsConstructor
public class JdbcRedditPostRepository {

    private final JdbcTemplate jdbcTemplate;

    private static final RowMapper<RedditPostEntity> ROW_MAPPER = JdbcRedditPostRepository::mapRow;

    public Optional<RedditPostEntity> findLatestByPostId(String postId) {
        List<RedditPostEntity> results = jdbcTemplate.query(
                "SELECT id, post_id, title, content, upvotes, comments, subreddit, created_at, last_seen_at, version, processed_at " +
                        "FROM reddit_posts WHERE post_id = ? ORDER BY version DESC LIMIT 1",
                ROW_MAPPER,
                postId
        );
        return results.stream().findFirst();
    }

    public RedditPostEntity insert(RawRedditPost post) {
        RedditPostEntity entity = RedditPostEntity.fromRawPost(post, 1);
        entity.setId(UUID.randomUUID());

        jdbcTemplate.update(
                "INSERT INTO reddit_posts (id, post_id, title, content, upvotes, comments, subreddit, created_at, last_seen_at, version, processed_at) " +
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                entity.getId(),
                entity.getPostId(),
                entity.getTitle(),
                entity.getContent(),
                entity.getUpvotes(),
                entity.getComments(),
                entity.getSubreddit(),
                toTimestamp(entity.getCreatedAt()),
                toTimestamp(entity.getLastSeenAt()),
                entity.getVersion(),
                toTimestamp(entity.getProcessedAt())
        );
        return entity;
    }

    public RedditPostEntity update(RedditPostEntity existing, RawRedditPost post) {
        int nextVersion = existing.getVersion() + 1;
        RedditPostEntity updated = RedditPostEntity.fromRawPost(post, nextVersion);
        updated.setId(existing.getId());

        jdbcTemplate.update(
                "UPDATE reddit_posts SET title = ?, content = ?, upvotes = ?, comments = ?, subreddit = ?, " +
                        "created_at = ?, last_seen_at = ?, version = ?, processed_at = ? WHERE id = ?",
                updated.getTitle(),
                updated.getContent(),
                updated.getUpvotes(),
                updated.getComments(),
                updated.getSubreddit(),
                toTimestamp(updated.getCreatedAt()),
                toTimestamp(updated.getLastSeenAt()),
                updated.getVersion(),
                toTimestamp(updated.getProcessedAt()),
                updated.getId()
        );
        return updated;
    }

    public RedditPostEntity touchLastSeen(RedditPostEntity existing) {
        Instant now = Instant.now();
        jdbcTemplate.update(
                "UPDATE reddit_posts SET last_seen_at = ? WHERE id = ?",
                toTimestamp(now),
                existing.getId()
        );

        existing.setLastSeenAt(now);
        return existing;
    }

    private static RedditPostEntity mapRow(ResultSet rs, int rowNum) throws SQLException {
        return RedditPostEntity.builder()
                .id(rs.getObject("id", UUID.class))
                .postId(rs.getString("post_id"))
                .title(rs.getString("title"))
                .content(rs.getString("content"))
                .upvotes(rs.getInt("upvotes"))
                .comments(rs.getInt("comments"))
                .subreddit(rs.getString("subreddit"))
                .createdAt(fromTimestamp(rs.getTimestamp("created_at")))
                .lastSeenAt(fromTimestamp(rs.getTimestamp("last_seen_at")))
                .version(rs.getInt("version"))
                .processedAt(fromTimestamp(rs.getTimestamp("processed_at")))
                .build();
    }

    private static @Nullable Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }

    private static @Nullable Instant fromTimestamp(Timestamp timestamp) {
        return timestamp == null ? null : timestamp.toInstant();
    }
}