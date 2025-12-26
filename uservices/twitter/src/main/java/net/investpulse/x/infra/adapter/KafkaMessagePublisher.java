package net.investpulse.x.infra.adapter;

import lombok.RequiredArgsConstructor;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.MessagePublisher;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;

/**
 * Kafka-specific implementation of the MessagePublisher port.
 * Wraps Spring Kafka infrastructure and isolates it from business logic.
 */
@RequiredArgsConstructor
public class KafkaMessagePublisher implements MessagePublisher {

    private static final int DEFAULT_PARTITIONS = 1;
    private static final short DEFAULT_REPLICATION_FACTOR = 1;

    private final KafkaTemplate<String, RawTweet> kafkaTemplate;
    private final KafkaAdmin kafkaAdmin;

    @Override
    public void publish(String topic, String key, RawTweet value) {
        kafkaTemplate.send(topic, key, value);
    }

    @Override
    public void ensureTopicExists(String topicName) {
        var newTopic = new NewTopic(topicName, DEFAULT_PARTITIONS, DEFAULT_REPLICATION_FACTOR);
        kafkaAdmin.createOrModifyTopics(newTopic);
    }
}
