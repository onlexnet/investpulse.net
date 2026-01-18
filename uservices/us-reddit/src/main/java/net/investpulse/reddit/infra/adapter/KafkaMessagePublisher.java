package net.investpulse.reddit.infra.adapter;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.common.dto.ScoredRedditPost;
import net.investpulse.reddit.domain.port.MessagePublisher;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.time.Instant;

/**
 * Kafka-based message publisher for Reddit posts.
 * Publishes both raw and scored posts to separate topics.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class KafkaMessagePublisher implements MessagePublisher {

    private final KafkaTemplate<String, RawRedditPost> rawPostTemplate;
    private final KafkaTemplate<String, ScoredRedditPost> scoredPostTemplate;

    @Override
    public void publishRawPost(RawRedditPost post) {
        String topic = String.format("reddit-raw-%s", 
                post.tickers().stream().findFirst().orElse("UNKNOWN"));
        rawPostTemplate.send(topic, post.id(), post)
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        log.error("Failed to publish raw post {} to topic {}", post.id(), topic, ex);
                    } else {
                        log.debug("Published raw post {} to {}", post.id(), topic);
                    }
                });
    }

    @Override
    public void publishScoredPost(String postId, String ticker, double sentimentScore,
                                 double weightedScore, int upvotes, int comments, Instant timestamp) {
        String topic = String.format("reddit-scored-%s", ticker);
        
        ScoredRedditPost scoredPost = new ScoredRedditPost(
                postId,
                ticker,
                sentimentScore,
                weightedScore,
                upvotes,
                comments,
                timestamp,  // Use original timestamp from Reddit API
                "reddit"
        );

        scoredPostTemplate.send(topic, postId, scoredPost)
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        log.error("Failed to publish scored post {} to topic {}", postId, topic, ex);
                    } else {
                        log.debug("Published scored post {} to {}", postId, topic);
                    }
                });
    }
}
