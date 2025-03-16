package onlexnet.webapi;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.ExecutionException;

import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.junit.jupiter.api.Test;

public class KafkaTest {

    private final String bootstrapServers = "localhost:9094";

    private static Properties loadConfig(final String configFile) throws IOException {
        if (!Files.exists(Paths.get(configFile))) {
            throw new IOException(configFile + " not found.");
        }
        final Properties cfg = new Properties();
        try (InputStream inputStream = new FileInputStream(configFile)) {
            cfg.load(inputStream);
        }
        return cfg;
    }

    // @Test
    void shouldUseKafka() throws IOException, InterruptedException, ExecutionException {
        final Properties props = loadConfig("config.properties");

        // Konfiguracja producenta
        var adminProps = new Properties();
        adminProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        adminProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        adminProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // temporal topic
        var temporalTopic = "temp-topic-" + UUID.randomUUID();
        String messageKey = "test-key";
        String messageValue = "Hello, Kafka!";

        // Konfiguracja producenta
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // Konfiguracja konsumenta
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "test-group-" + UUID.randomUUID());
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        try (var adminClient = AdminClient.create(adminProps)) {
            var newTopic = new NewTopic(temporalTopic, 1, (short) 1);
            adminClient.createTopics(Collections.singleton(newTopic)).all().get();

            try (var producer = new KafkaProducer<String, String>(producerProps);
                    var consumer = new KafkaConsumer<String, String>(consumerProps)) {

                consumer.subscribe(Collections.singletonList(temporalTopic));

                // Wysłanie wiadomości
                var result = producer.send(new ProducerRecord<>(temporalTopic, messageKey, messageValue));
                result.get();

                producer.flush();

                var receivedRecord = (ConsumerRecord<String, String>) null;
                long timeout = System.currentTimeMillis() + 10000; // 5 sekund timeout

                while (System.currentTimeMillis() < timeout) {
                    var records = consumer.poll(Duration.ofMillis(100));
                    if (!records.isEmpty()) {
                        receivedRecord = records.iterator().next();
                        break;
                    }
                }

                // Weryfikacja
                assertEquals(messageKey, receivedRecord.key());
                assertEquals(messageValue, receivedRecord.value());
            }
            // Po użyciu
            adminClient.deleteTopics(Collections.singleton("my-temporary-topic")).all().get();
        }
    }
}
