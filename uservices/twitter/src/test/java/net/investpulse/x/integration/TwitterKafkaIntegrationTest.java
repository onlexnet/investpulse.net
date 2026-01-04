package net.investpulse.x.integration;

import net.investpulse.common.dto.RawTweet;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.test.context.TestPropertySource;

import java.time.Duration;
import java.time.Instant;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test for Kafka message publishing and consumption in Twitter service.
 * Uses @SpringBootTest to test with Spring Boot's auto-configured Kafka beans.
 * Tests the full flow: publish → consume → cleanup.
 * Uses the same Kafka instance as configured in application.yml (localhost:9092).
 */
@SpringBootTest
@TestPropertySource(properties = {
    "spring.cloud.config.enabled=false",
    "spring.cloud.bus.enabled=false",
    "spring.kafka.consumer.properties.spring.json.trusted.packages=*",
    "spring.kafka.consumer.properties.spring.json.value.default.type=net.investpulse.common.dto.RawTweet",
    "twitter.bearer-token=TEST_TOKEN",
    "twitter.accounts-to-follow=testuser"
})
class TwitterKafkaIntegrationTest {

    private static final Duration POLL_TIMEOUT = Duration.ofSeconds(10);
    private static final String TEST_TOPIC_PREFIX = "test-ticker-";

    @Autowired
    private KafkaTemplate<String, RawTweet> kafkaTemplate;

    @Autowired
    private KafkaAdmin kafkaAdmin;

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    private String testTopic;
    private KafkaConsumer<String, RawTweet> consumer;
    private AdminClient adminClient;

    @BeforeEach
    void setUp() {
        // Generate unique topic name for test isolation
        testTopic = TEST_TOPIC_PREFIX + UUID.randomUUID();

        // Create topic
        // kafkaAdmin.createOrModifyTopics(
        //     new org.apache.kafka.clients.admin.NewTopic(testTopic, 1, (short) 1)
        // );

        // Configure consumer with same settings as application.yml
        Map<String, Object> consumerProps = new HashMap<>();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "test-group-" + UUID.randomUUID());
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
        consumerProps.put(JsonDeserializer.TRUSTED_PACKAGES, "*");
        consumerProps.put(JsonDeserializer.VALUE_DEFAULT_TYPE, RawTweet.class.getName());

        consumer = new KafkaConsumer<>(consumerProps);

        // Assign to partition 0 (faster than subscribe for tests)
        TopicPartition partition = new TopicPartition(testTopic, 0);
        consumer.assign(Collections.singleton(partition));
        consumer.seekToBeginning(Collections.singleton(partition));

        // Create admin client for topic management
        Map<String, Object> adminProps = new HashMap<>();
        adminProps.put("bootstrap.servers", bootstrapServers);
        adminClient = AdminClient.create(adminProps);
    }

    @AfterEach
    void tearDown() throws Exception {
        // Close consumer
        if (consumer != null) {
            consumer.close();
        }

        // Delete test topic
        if (testTopic != null && adminClient != null) {
            adminClient.deleteTopics(Collections.singleton(testTopic)).all().get();
            
            // Verify topic deletion
            Set<String> topics = adminClient.listTopics().names().get();
            assertThat(topics).doesNotContain(testTopic);
        }

        // Close admin client
        if (adminClient != null) {
            adminClient.close();
        }
    }

    @Test
    void shouldPublishConsumeAndDeleteTopic() {
        // Given: A raw tweet to publish
        RawTweet tweet = new RawTweet(
            "tweet-123",
            "Test tweet about $AAPL and $TSLA",
            "user123",
            "testuser",
            Instant.now(),
            "X API",
            "@TestPublisher",
            Set.of("AAPL", "TSLA")
        );

        // When: Publish message using autowired KafkaTemplate (uses application.yml config)
        kafkaTemplate.send(testTopic, "AAPL", tweet);

        // Then: Message should be consumed successfully
        var records = consumer.poll(POLL_TIMEOUT);
        
        assertThat(records).isNotEmpty();
        assertThat(records.count()).isEqualTo(1);
        
        var record = records.iterator().next();
        assertThat(record.topic()).isEqualTo(testTopic);
        assertThat(record.key()).isEqualTo("AAPL");
        assertThat(record.value()).isNotNull();
        assertThat(record.value().id()).isEqualTo("tweet-123");
        assertThat(record.value().text()).isEqualTo("Test tweet about $AAPL and $TSLA");
        assertThat(record.value().authorUsername()).isEqualTo("testuser");
        assertThat(record.value().publisher()).isEqualTo("@TestPublisher");
        assertThat(record.value().tickers()).containsExactlyInAnyOrder("AAPL", "TSLA");
        
        // Topic cleanup will be verified in @AfterEach
    }

    @Test
    void shouldPublishMultipleMessagesToTestTopic() {
        // Given: Multiple tweets
        RawTweet tweet1 = new RawTweet(
            "tweet-1", "First $BTC tweet", "user1", "user1",
            Instant.now(), "X API", "@Publisher1", Set.of("BTC")
        );
        
        RawTweet tweet2 = new RawTweet(
            "tweet-2", "Second $BTC tweet", "user2", "user2",
            Instant.now(), "X API", "@Publisher2", Set.of("BTC")
        );

        // When: Publish multiple messages
        kafkaTemplate.send(testTopic, "BTC", tweet1);
        kafkaTemplate.send(testTopic, "BTC", tweet2);

        // Then: Both messages should be consumed
        var records = consumer.poll(POLL_TIMEOUT);
        
        assertThat(records).hasSize(2);
        
        var tweets = new ArrayList<RawTweet>();
        records.forEach(record -> {
            assertThat(record.topic()).isEqualTo(testTopic);
            assertThat(record.key()).isEqualTo("BTC");
            tweets.add(record.value());
        });
        
        assertThat(tweets).extracting(RawTweet::id)
            .containsExactlyInAnyOrder("tweet-1", "tweet-2");
    }
}
