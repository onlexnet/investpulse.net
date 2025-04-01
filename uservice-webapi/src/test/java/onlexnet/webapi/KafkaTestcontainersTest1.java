package onlexnet.webapi;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.ByteArrayDeserializer;
import org.apache.kafka.common.serialization.ByteArraySerializer;
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
import org.springframework.kafka.core.KafkaAdmin.NewTopics;
import org.springframework.test.context.ActiveProfiles;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.kafka.KafkaContainer;

import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import onlexnet.webapi.avro.MyMessage;

@Testcontainers
@SpringBootTest(classes = KafkaTestcontainersTest1.KafkaTestConfig.class)
@ActiveProfiles("test")
public class KafkaTestcontainersTest1 {

  static final String TEST_TOPIC_STRING = "topic-string-aaa";

  static Network network = Network.newNetwork();

  @Container
  static KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0").withNetwork(network)
      .withListener("kafka:19092");

  @Autowired
  KafkaTemplate<String, String> kafkaTemplate;

  private final CountDownLatch latch = new CountDownLatch(10);
  private String receivedMessage1;

  @KafkaListener(topics = TEST_TOPIC_STRING, groupId = TEST_TOPIC_STRING, containerFactory = "stringKafkaListenerContainerFactory1")
  public void listen(String message) {
    this.receivedMessage1 = message;
    latch.countDown();
  }

  @Test
  public void testKafkaSendAndReceiveString() throws Exception {
    var message = "Hello, Kafka!";
    kafkaTemplate.send(TEST_TOPIC_STRING, message).join();

    boolean messageReceived = latch.await(100, TimeUnit.SECONDS);

    assertThat(messageReceived).isTrue();
    assertThat(receivedMessage1).isEqualTo(message);
  }

  @EnableKafka
  @Configuration
  static class KafkaTestConfig {

    static KafkaContainer kafkaContainer = KafkaTestcontainersTest1.kafka;

    
    @Bean
    public ProducerFactory<String, String> stringProducerFactory() {
      Map<String, Object> props = new HashMap<>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest1.kafka.getBootstrapServers());
      props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplateString(ProducerFactory<String, String> producerFactory) {
      return new KafkaTemplate<>(producerFactory);
    }

    @Bean
    public ConsumerFactory<String, String> stringConsumerFactory() {
      var props = new HashMap<String, Object>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaContainer.getBootstrapServers());
      // props.put("group.id", "string-group");
      props.put("auto.offset.reset", "latest");
      props.put("key.deserializer", StringDeserializer.class);
      props.put("value.deserializer", StringDeserializer.class);
      return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> stringKafkaListenerContainerFactory1() {
      var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
      factory.setConsumerFactory(stringConsumerFactory());
      factory.setConcurrency(1);
      return factory;
    }

    @Bean
    public NewTopic newTopics() {
      return new NewTopic(TEST_TOPIC_STRING, 1, (short) 1);
    }

  }
}
