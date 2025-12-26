package net.investpulse.x.infra.adapter;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.MessagePublisher;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.testcontainers.kafka.KafkaContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.time.Duration;
import java.time.Instant;
import java.util.*;

import static org.assertj.core.api.Assertions.assertThat;

@Testcontainers
class KafkaMessagePublisherIntegrationTest {

    private static final String KAFKA_IMAGE = "apache/kafka:latest";
    private static final String TEST_GROUP_ID = "test-group";
    private static final String OFFSET_RESET_EARLIEST = "earliest";
    private static final String TRUSTED_PACKAGES_ALL = "*";
    private static final Duration POLL_TIMEOUT = Duration.ofSeconds(10);

    @Container
    static final KafkaContainer kafka = new KafkaContainer(
            DockerImageName.parse(KAFKA_IMAGE)
    );

    private MessagePublisher messagePublisher;
    private KafkaConsumer<String, RawTweet> consumer;
    private AdminClient adminClient;

    @BeforeEach
    void setUp() {
        var bootstrapServers = kafka.getBootstrapServers();

        // Configure producer
        var producerProps = createProducerConfig(bootstrapServers);
        var producerFactory = new DefaultKafkaProducerFactory<String, RawTweet>(producerProps);
        var kafkaTemplate = new KafkaTemplate<>(producerFactory);

        // Configure KafkaAdmin
        var adminProps = createAdminConfig(bootstrapServers);
        var kafkaAdmin = new KafkaAdmin(adminProps);

        // Create adapter
        messagePublisher = new KafkaMessagePublisher(kafkaTemplate, kafkaAdmin);

        // Configure consumer
        var consumerProps = createConsumerConfig(bootstrapServers);
        consumer = new KafkaConsumer<>(consumerProps);

        // Configure admin client
        adminClient = AdminClient.create(adminProps);
    }

    private static Map<String, Object> createProducerConfig(String bootstrapServers) {
        return Map.of(
                "bootstrap.servers", bootstrapServers,
                "key.serializer", "org.apache.kafka.common.serialization.StringSerializer",
                "value.serializer", "org.springframework.kafka.support.serializer.JsonSerializer"
        );
    }

    private static Map<String, Object> createAdminConfig(String bootstrapServers) {
        return Map.of(
                AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers
        );
    }

    private static Map<String, Object> createConsumerConfig(String bootstrapServers) {
        return Map.of(
                ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers,
                ConsumerConfig.GROUP_ID_CONFIG, TEST_GROUP_ID,
                ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, OFFSET_RESET_EARLIEST,
                ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class,
                ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class,
                JsonDeserializer.TRUSTED_PACKAGES, TRUSTED_PACKAGES_ALL,
                JsonDeserializer.VALUE_DEFAULT_TYPE, RawTweet.class.getName()
        );
    }

    @AfterEach
    void tearDown() {
        if (consumer != null) {
            consumer.close();
        }
        if (adminClient != null) {
            adminClient.close();
        }
    }

    @Test
    void shouldCreateTopicWhenEnsureTopicExists() throws Exception {
        String topicName = "ticker-TEST";

        messagePublisher.ensureTopicExists(topicName);

        // Verify topic exists
        var topics = adminClient.listTopics().names().get();
        assertThat(topics).contains(topicName);
    }

    @Test
    void shouldPublishMessageToTopic() throws Exception {
        String topicName = "ticker-AAPL";
        RawTweet tweet = new RawTweet(
            "tweet-123",
            "Test tweet about $AAPL",
            "user123",
            "testuser",
            Instant.now(),
            "X API",
            "@TestPublisher",
            Set.of("AAPL")
        );

        // Ensure topic exists and publish
        messagePublisher.ensureTopicExists(topicName);
        messagePublisher.publish(topicName, "AAPL", tweet);

        // Subscribe and consume
        consumer.subscribe(List.of(topicName));
        var records = consumer.poll(POLL_TIMEOUT);

        assertThat(records).isNotEmpty();
        
        ConsumerRecord<String, RawTweet> record = records.iterator().next();
        assertThat(record.topic()).isEqualTo(topicName);
        assertThat(record.key()).isEqualTo("AAPL");
        assertThat(record.value()).isNotNull();
        assertThat(record.value().id()).isEqualTo("tweet-123");
        assertThat(record.value().text()).isEqualTo("Test tweet about $AAPL");
        assertThat(record.value().tickers()).containsExactly("AAPL");
    }

    @Test
    void shouldPublishMultipleMessagesToSameTopic() throws Exception {
        String topicName = "ticker-TSLA";
        
        RawTweet tweet1 = new RawTweet(
            "tweet-1", "First $TSLA tweet", "user1", "user1",
            Instant.now(), "X API", "@Publisher1", Set.of("TSLA")
        );
        
        RawTweet tweet2 = new RawTweet(
            "tweet-2", "Second $TSLA tweet", "user2", "user2",
            Instant.now(), "X API", "@Publisher2", Set.of("TSLA")
        );

        // Ensure topic exists and publish
        messagePublisher.ensureTopicExists(topicName);
        messagePublisher.publish(topicName, "TSLA", tweet1);
        messagePublisher.publish(topicName, "TSLA", tweet2);

        // Subscribe and consume
        consumer.subscribe(List.of(topicName));
        var records = consumer.poll(POLL_TIMEOUT);

        assertThat(records).hasSize(2);
        
        var tweets = new ArrayList<RawTweet>();
        records.forEach(record -> tweets.add(record.value()));
        
        assertThat(tweets).extracting(RawTweet::id)
            .containsExactlyInAnyOrder("tweet-1", "tweet-2");
    }
}
