package net.investpulse.reddit.service;

import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.reddit.domain.port.RedditPostRepository;
import net.investpulse.reddit.infra.persistence.entity.RedditPostEntity;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.time.Instant;
import java.util.Optional;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(properties = {
    "spring.task.scheduling.enabled=false",
    "spring.scheduling.enabled=false",
    "spring.cloud.stream.enabled=false",
    "spring.cloud.bus.enabled=false",
    "reddit.scheduler.enabled=false"
})
@Testcontainers
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class DatabaseDeduplicationServiceIntegrationTest {

    @Container
    private static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @DynamicPropertySource
    static void overrideDataSourceProps(DynamicPropertyRegistry registry) {
        postgres.start();
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private DatabaseDeduplicationService service;

    @Autowired
    private RedditPostRepository repository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    void cleanDatabase() {
        jdbcTemplate.update("DELETE FROM reddit_posts");
    }

    @Test
    void savesNewPostWithVersionOne() {
        RawRedditPost post = samplePost("p1", 10, 2, "Title", "Body");

        DatabaseDeduplicationService.DeduplicationResult result = service.checkAndSavePost(post);

        assertThat(result.status()).isEqualTo(DatabaseDeduplicationService.PostStatus.NEW);
        assertThat(result.version()).isEqualTo(1);

        Optional<RedditPostEntity> persisted = repository.findLatestVersion("p1");
        assertThat(persisted).isPresent();
        assertThat(persisted.get().getVersion()).isEqualTo(1);
    }

    @Test
    void updatesPostWhenChanged() {
        RawRedditPost initial = samplePost("p2", 5, 1, "First", "Body");
        RawRedditPost updated = samplePost("p2", 15, 3, "First", "Body");

        service.checkAndSavePost(initial);
        DatabaseDeduplicationService.DeduplicationResult result = service.checkAndSavePost(updated);

        assertThat(result.status()).isEqualTo(DatabaseDeduplicationService.PostStatus.UPDATED);
        assertThat(result.version()).isEqualTo(2);

        RedditPostEntity persisted = repository.findLatestVersion("p2").orElseThrow();
        assertThat(persisted.getUpvotes()).isEqualTo(15);
        assertThat(persisted.getComments()).isEqualTo(3);
        assertThat(persisted.getVersion()).isEqualTo(2);
    }

    @Test
    void touchesLastSeenWhenUnchanged() {
        RawRedditPost post = samplePost("p3", 7, 1, "Same", "Body");

        service.checkAndSavePost(post);
        RedditPostEntity first = repository.findLatestVersion("p3").orElseThrow();

        service.checkAndSavePost(post);
        RedditPostEntity second = repository.findLatestVersion("p3").orElseThrow();

        assertThat(second.getVersion()).isEqualTo(1);
        assertThat(second.getLastSeenAt()).isAfterOrEqualTo(first.getLastSeenAt());
    }

    private RawRedditPost samplePost(String id, int upvotes, int comments, String title, String content) {
        return new RawRedditPost(
                id,
                title,
                content,
                upvotes,
                comments,
                Instant.parse("2024-01-01T00:00:00Z"),
                "stocks",
                Set.of("AAPL"),
                null,
                null
        );
    }
}