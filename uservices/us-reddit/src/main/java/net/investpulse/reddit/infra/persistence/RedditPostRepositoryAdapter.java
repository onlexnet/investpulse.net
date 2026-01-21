package net.investpulse.reddit.infra.persistence;

import lombok.RequiredArgsConstructor;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostRepository;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.stereotype.Component;

import java.util.Optional;

/**
 * Adapter implementation of RedditPostRepository using JdbcTemplate.
 */
@Component
@RequiredArgsConstructor
public class RedditPostRepositoryAdapter implements RedditPostRepository {

    private final JdbcRedditPostRepository jdbcRepository;

    @Override
    public Optional<RedditPostEntity> findLatestVersion(String postId) {
        return jdbcRepository.findLatestByPostId(postId);
    }

    @Override
    public RedditPostEntity saveNew(RawRedditPost post) {
        return jdbcRepository.insert(post);
    }

    @Override
    public RedditPostEntity saveUpdated(RedditPostEntity existing, RawRedditPost post) {
        return jdbcRepository.update(existing, post);
    }

    @Override
    public RedditPostEntity touchLastSeen(RedditPostEntity existing) {
        return jdbcRepository.touchLastSeen(existing);
    }
}
