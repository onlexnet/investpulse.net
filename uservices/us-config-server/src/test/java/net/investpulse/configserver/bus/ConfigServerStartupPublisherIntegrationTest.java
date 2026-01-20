package net.investpulse.configserver.bus;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.errors.UnknownTopicOrPartitionException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test for ConfigServerStartupPublisher.
 * Verifies that a RefreshRemoteApplicationEvent is published to Kafka when Config Server starts.
 * <p>
 * Uses a randomized test topic to ensure test isolation and parallel safety.
 * Requires Kafka running on localhost:9092.
 */
@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.NONE,
    properties = {
        // Enable Kafka (override test defaults)
        "spring.kafka.bootstrap-servers=localhost:9092",
        "spring.kafka.consumer.group-id=config-server-test-group",
        
        // Disable Azure services
        "spring.cloud.azure.keyvault.secret.property-source-enabled=false",
        "spring.cloud.azure.autoconfigure.enabled=false"
    }
)
class ConfigServerStartupPublisherIntegrationTest {

    private static final String TEST_TOPIC = "springCloudBus-test-" + UUID.randomUUID();

    private static KafkaConsumer<String, String> consumer;
    private static ObjectMapper objectMapper;
    private static AdminClient adminClient;

    @DynamicPropertySource
    static void dynamicProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.cloud.stream.bindings.springCloudBus-out-0.destination", () -> TEST_TOPIC);
        registry.add("spring.cloud.bus.destination", () -> TEST_TOPIC);
    }

    @BeforeAll
    static void setUp() {
        log.info("Setting up Kafka consumer for test topic '{}'", TEST_TOPIC);
        
        // Configure ObjectMapper for JSON parsing
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        
        // Create AdminClient for topic cleanup
        Map<String, Object> adminConfig = Map.of(
            AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092"
        );
        adminClient = AdminClient.create(adminConfig);
        
        // Configure Kafka consumer with unique group ID to avoid offset conflicts
        Map<String, Object> consumerConfig = Map.of(
            ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092",
            ConsumerConfig.GROUP_ID_CONFIG, "test-group-" + UUID.randomUUID(),  // Unique group per test run
            ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest",  // Read from beginning for new group
            ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class,
            ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class
        );
        
        consumer = new KafkaConsumer<>(consumerConfig);
        consumer.subscribe(List.of(TEST_TOPIC));
        
        log.info("Kafka consumer configured and subscribed to '{}'", TEST_TOPIC);
    }

    @AfterAll
    static void tearDown() {
        // Close consumer first to avoid any lingering subscriptions
        if (consumer != null) {
            try {
                consumer.unsubscribe();
            } catch (Exception e) {
                log.debug("Consumer unsubscribe encountered an issue: {}", e.getMessage());
            }
            consumer.close(Duration.ofSeconds(5));
            log.info("Kafka consumer closed");
        }

        // Delete test topic
        if (adminClient != null) {
            try {
                adminClient
                    .deleteTopics(List.of(TEST_TOPIC))
                    .all()
                    .get(15, TimeUnit.SECONDS);
                log.info("Deleted test topic: {}", TEST_TOPIC);
            } catch (ExecutionException ee) {
                if (ee.getCause() instanceof UnknownTopicOrPartitionException) {
                    log.info("Test topic already deleted or missing: {}", TEST_TOPIC);
                } else {
                    log.warn("Failed to delete topic {}: {}", TEST_TOPIC, ee.getMessage());
                }
            } catch (Exception e) {
                log.warn("Failed to delete topic {}: {}", TEST_TOPIC, e.getMessage());
            } finally {
                adminClient.close(Duration.ofSeconds(5));
            }
        }
    }

    @Test
    void shouldPublishRefreshEventToKafkaOnStartup() throws Exception {
        log.info("Polling Kafka topic '{}' for RefreshRemoteApplicationEvent", TEST_TOPIC);
        
        // Poll for messages (published during ApplicationReadyEvent)
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(10));
        
        assertThat(records).isNotEmpty()
            .withFailMessage("Expected at least one message in topic '" + TEST_TOPIC + "'");
        
        var record = records.iterator().next();
        String json = record.value();
        
        log.info("Received message from Kafka: {}", json);
        
        // Parse as JSON and verify structure (Spring Cloud Bus uses 'type' field, not @class)
        var jsonNode = objectMapper.readTree(json);
        
        assertThat(jsonNode.has("type")).isTrue()
            .withFailMessage("Expected 'type' field in JSON");
        assertThat(jsonNode.get("type").asText())
            .isEqualTo("RefreshRemoteApplicationEvent")
            .withFailMessage("Expected type='RefreshRemoteApplicationEvent' but got '%s'", 
                jsonNode.get("type").asText());
        
        assertThat(jsonNode.has("originService")).isTrue()
            .withFailMessage("Expected 'originService' field in JSON");
        assertThat(jsonNode.get("originService").asText())
            .isEqualTo("config-server")
            .withFailMessage("Expected originService='config-server' but got '%s'", 
                jsonNode.get("originService").asText());
        
        assertThat(jsonNode.has("destinationService")).isTrue()
            .withFailMessage("Expected 'destinationService' field in JSON");
        assertThat(jsonNode.get("destinationService").asText())
            .isEqualTo("**")
            .withFailMessage("Expected destinationService='**' but got '%s'", 
                jsonNode.get("destinationService").asText());
        
        log.info("✓ RefreshRemoteApplicationEvent verified: type={}, origin={}, destination={}", 
            jsonNode.get("type").asText(),
            jsonNode.get("originService").asText(),
            jsonNode.get("destinationService").asText());
    }
}
