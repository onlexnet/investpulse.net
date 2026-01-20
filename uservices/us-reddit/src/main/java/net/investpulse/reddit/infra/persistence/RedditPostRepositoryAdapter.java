package net.investpulse.reddit.infra.persistence;

import lombok.RequiredArgsConstructor;
import net.investpulse.reddit.domain.port.RedditPostRepository;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.springframework.stereotype.Component;

import java.util.Optional;

/**
 * Adapter implementation of RedditPostRepository using Spring Data JPA.
 * Follows hexagonal architecture pattern.
 */
@Component
@RequiredArgsConstructor
public class RedditPostRepositoryAdapter implements RedditPostRepository {

    private final JpaRedditPostRepository jpaRepository;

    @Override
    public Optional<RedditPostEntity> findLatestVersion(String postId) {
        return jpaRepository.findLatestByPostId(postId);
    }

    @Override
    public RedditPostEntity save(RedditPostEntity entity) {
        return jpaRepository.save(entity);
    }
}
