package net.investpulse.reddit;

import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawRedditPost;
import net.investpulse.common.dto.ScoredRedditPost;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.web.client.RestClient;

/**
 * Spring Boot configuration for Reddit sentiment analysis service.
 * Enables scheduling, config server integration, and Kafka producers.
 */
@Slf4j
@SpringBootApplication
@EnableScheduling
@ConfigurationPropertiesScan
public class RedditRootConfigurer {

    /**
     * RestClient bean for HTTP requests to Reddit API.
     */
    @Bean
    public RestClient restClient() {
        return RestClient.builder().build();
    }

    /**
     * Kafka template for publishing raw Reddit posts.
     */
    @Bean
    public KafkaTemplate<String, RawRedditPost> rawRedditPostKafkaTemplate(
            org.springframework.kafka.core.ProducerFactory<String, RawRedditPost> producerFactory) {
        return new KafkaTemplate<>(producerFactory);
    }

    /**
     * Kafka template for publishing scored Reddit posts.
     */
    @Bean
    public KafkaTemplate<String, ScoredRedditPost> scoredRedditPostKafkaTemplate(
            org.springframework.kafka.core.ProducerFactory<String, ScoredRedditPost> producerFactory) {
        return new KafkaTemplate<>(producerFactory);
    }
}
