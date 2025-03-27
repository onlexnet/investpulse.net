package onlexnet.webapi;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.test.context.ActiveProfiles;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.kafka.KafkaContainer;
import org.testcontainers.utility.DockerImageName;

@Testcontainers
@SpringBootTest(classes = KafkaTestcontainersTest.KafkaTestConfig.class)
@ActiveProfiles("test")
public class KafkaTestcontainersTest {

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
    var message = "Hello, Kafka!";
    kafkaTemplate.send("test-topic", message);

    boolean messageReceived = latch.await(5, TimeUnit.SECONDS);

    assertThat(messageReceived).isTrue();
    assertThat(receivedMessage).isEqualTo(message);
  }

  @EnableKafka
  @Configuration
  static class KafkaTestConfig {

    @Bean
    public ProducerFactory<String, String> producerFactory() {
      Map<String, Object> configProps = new HashMap<>();
      configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest.kafka.getBootstrapServers());
      configProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      configProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      return new DefaultKafkaProducerFactory<>(configProps);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplate() {
      return new KafkaTemplate<>(producerFactory());
    }

    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
      Map<String, Object> configProps = new HashMap<>();
      configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest.kafka.getBootstrapServers());
      configProps.put("group.id", "test-group");
      configProps.put("auto.offset.reset", "earliest");
      configProps.put("key.deserializer", StringDeserializer.class);
      configProps.put("value.deserializer", StringDeserializer.class);
      return new DefaultKafkaConsumerFactory<>(configProps);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
      ConcurrentKafkaListenerContainerFactory<String, String> factory = new ConcurrentKafkaListenerContainerFactory<>();
      factory.setConsumerFactory(consumerFactory());
      return factory;
    }

    @Bean
    public NewTopic testTopic() {
      return new NewTopic("test-topic", 1, (short) 1);
    }
  }
}
