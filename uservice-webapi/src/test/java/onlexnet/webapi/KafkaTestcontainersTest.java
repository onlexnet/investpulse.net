package onlexnet.webapi;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.kafka.KafkaContainer;

@Testcontainers
@SpringBootTest
public class KafkaTestcontainersTest {

    // Testcontainers Kafka
    @Container
    @ServiceConnection
    static KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0");

    @Autowired
    KafkaTemplate<String, String> kafkaTemplate;

    private final CountDownLatch latch = new CountDownLatch(1);
    private String receivedMessage;

    @KafkaListener(topics = "test-topic", groupId = "test-group")
    public void listen(String message) {
        this.receivedMessage = message;
        latch.countDown();
    }

    @Test
    public void testKafkaSendAndReceive() throws Exception {
        String message = "Hello, Kafka!";
        kafkaTemplate.send("test-topic", message);

        boolean messageReceived = latch.await(5, TimeUnit.SECONDS);

        assertThat(messageReceived).isTrue();
        assertThat(receivedMessage).isEqualTo(message);
    }
}