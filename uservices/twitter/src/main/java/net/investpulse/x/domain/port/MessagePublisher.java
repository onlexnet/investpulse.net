package net.investpulse.x.domain.port;

import net.investpulse.common.dto.RawTweet;

/**
 * Port interface for publishing messages to external messaging systems.
 * Abstracts message publishing infrastructure from business logic.
 * <p>
 * This interface follows hexagonal architecture principles, allowing
 * the domain logic to remain independent of specific messaging implementations.
 */
public interface MessagePublisher {

    /**
     * Publishes a message to the specified topic.
     * <p>
     * This method uses fire-and-forget semantics for simplicity.
     * 
     * TODO: Consider returning CompletableFuture&lt;SendResult&gt; for async error handling
     * 
     * @param topic the target topic name
     * @param key the message key (used for partitioning)
     * @param value the message payload
     */
    void publish(String topic, String key, RawTweet value);

    /**
     * Ensures that a topic exists in the messaging system.
     * Creates the topic if it doesn't already exist.
     * 
     * @param topicName the name of the topic to ensure exists
     */
    void ensureTopicExists(String topicName);
}
