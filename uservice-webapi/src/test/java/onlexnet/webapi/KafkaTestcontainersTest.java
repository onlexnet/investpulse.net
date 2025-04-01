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
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.core.KafkaAdmin.NewTopics;
import org.springframework.test.annotation.DirtiesContext;
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
@SpringBootTest
@Import(KafkaTestcontainersTest.KafkaTestConfig.class)
@ActiveProfiles("test")
@DirtiesContext
public class KafkaTestcontainersTest {

  static final String TEST_TOPIC_STRING = "topic-3";
  static final String TEST_TOPIC_2 = "test-topic-2";
  static final String TEST_TOPIC_3 = "test-topic-3";
  static final int TIMEOUT = 100;

  static Network network = Network.newNetwork();

  @ServiceConnection
  @Container
  static KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0").withNetwork(network)
      .withListener("kafka:19092");

  @Container
  static GenericContainer<?> schemaRegistry = new GenericContainer<>("confluentinc/cp-schema-registry:7.4.0")
      .dependsOn(kafka)
      .withExposedPorts(8085)
      .withNetworkAliases("schemaregistry")
      .withNetwork(network)
      .withEnv("SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS", "PLAINTEXT://kafka:19092")
      .withEnv("SCHEMA_REGISTRY_LISTENERS", "http://0.0.0.0:8085")
      .withEnv("SCHEMA_REGISTRY_HOST_NAME", "schemaregistry")
      .withEnv("SCHEMA_REGISTRY_KAFKASTORE_SECURITY_PROTOCOL", "PLAINTEXT")
      .waitingFor(Wait.forHttp("/subjects"))
      .withStartupTimeout(Duration.ofSeconds(120));

  @Autowired
  KafkaTemplate<String, String> kafkaTemplate1;

  @Autowired
  KafkaTemplate<String, MyMessage> kafkaTemplate2;

  @Autowired
  KafkaTemplate<String, byte[]> kafkaTemplate3;

  private final CountDownLatch latch1 = new CountDownLatch(1);
  private String receivedMessage1;

  private final CountDownLatch latch2 = new CountDownLatch(1);
  private MyMessage receivedMessage2;

  private final CountDownLatch latch3 = new CountDownLatch(1);
  private byte[] receivedMessage3;

  @KafkaListener(topics = TEST_TOPIC_STRING, groupId = "test-group-1", containerFactory = "stringKafkaListenerContainerFactory")
  public void listen(String message) {
    this.receivedMessage1 = message;
    latch1.countDown();
  }

  @KafkaListener(topics = TEST_TOPIC_2, groupId = "test-group-2", containerFactory = "avroKafkaListenerContainerFactory")
  public void listen2(ConsumerRecord<String, MyMessage> record) {
    this.receivedMessage2 = record.value();
    latch2.countDown();
  }

  @KafkaListener(topics = TEST_TOPIC_3, groupId = "test-group-3", containerFactory = "byteKafkaListenerContainerFactory")
  public void listen3(ConsumerRecord<String, byte[]> record) {
    this.receivedMessage3 = record.value();
    latch3.countDown();
  }

  @Test
  public void testKafkaSendAndReceiveString() throws Exception {
    var message = "Hello, Kafka!";
    kafkaTemplate1.send(TEST_TOPIC_STRING, message).get();

    boolean messageReceived = latch1.await(TIMEOUT, TimeUnit.SECONDS);

    assertThat(messageReceived).isTrue();
    assertThat(receivedMessage1).isEqualTo(message);
  }

  // @Test
  public void testKafkaSendAndReceiveAvro() throws Exception {
    var message = new MyMessage(20010203, 1201);
    kafkaTemplate2.send(TEST_TOPIC_2, message);

    boolean messageReceived = latch2.await(TIMEOUT, TimeUnit.SECONDS);

    assertThat(messageReceived).isTrue();
    assertThat(receivedMessage2).isEqualTo(message);
  }

  @Test
  public void testKafkaSendAndReceiveBytes() throws Exception {
    var message = new byte[] { 42 };
    kafkaTemplate3.send(TEST_TOPIC_3, message);

    boolean messageReceived = latch3.await(TIMEOUT, TimeUnit.SECONDS);

    assertThat(messageReceived).isTrue();
    // assertThat(receivedMessage2).isEqualTo(message);
  }


  @EnableKafka
  @Configuration
  static class KafkaTestConfig {

    static KafkaContainer kafkaContainer = KafkaTestcontainersTest.kafka;

    
    @Bean
    public ProducerFactory<String, String> stringProducerFactory() {
      Map<String, Object> props = new HashMap<>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest.kafka.getBootstrapServers());
      props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      props.put("schema.registry.url",
          "http://%s:%d".formatted(schemaRegistry.getHost(), schemaRegistry.getMappedPort(8085)));
      return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public ProducerFactory<String, MyMessage> avroProducerFactory() {
      Map<String, Object> props = new HashMap<>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest.kafka.getBootstrapServers());
      props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
      props.put("schema.registry.url",
          "http://%s:%d".formatted(schemaRegistry.getHost(), schemaRegistry.getMappedPort(8085)));
      return new DefaultKafkaProducerFactory<>(props);
    }

   @Bean
    public ProducerFactory<String, byte[]> bytesProducerFactory() {
      var props = new HashMap<String, Object>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaTestcontainersTest.kafka.getBootstrapServers());
      props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
      props.put("schema.registry.url",
          "http://%s:%d".formatted(schemaRegistry.getHost(), schemaRegistry.getMappedPort(8085)));
      // !!! https://docs.spring.io/spring-kafka/reference/kafka/serdes.html
      props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteArraySerializer.class);
      return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public KafkaTemplate<String, String> kafkaTemplateString(ProducerFactory<String, String> producerFactory) {
      return new KafkaTemplate<>(producerFactory);
    }

    @Bean
    public KafkaTemplate<String, MyMessage> kafkaTemplate2() {
      return new KafkaTemplate<>(avroProducerFactory());
    }

    @Bean
    public KafkaTemplate<String, byte[]> kafkaTemplate3() {
      return new KafkaTemplate<>(bytesProducerFactory());
    }

    @Bean
    public ConsumerFactory<String, String> stringConsumerFactory() {
      var props = new HashMap<String, Object>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaContainer.getBootstrapServers());
      // props.put("group.id", "string-group");
      props.put("auto.offset.reset", "latest");
      props.put("key.deserializer", StringDeserializer.class);
      props.put("value.deserializer", StringDeserializer.class);
      props.put("schema.registry.url",
          "http://%s:%d".formatted(schemaRegistry.getHost(), schemaRegistry.getMappedPort(8085)));
      return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConsumerFactory<String, MyMessage> avroConsumerFactory() {
      var props = new HashMap<String, Object>();
      props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaContainer.getBootstrapServers());
      // props.put("group.id", "avro-group");
      props.put("auto.offset.reset", "latest");
      props.put("key.deserializer", StringDeserializer.class);
      props.put("value.deserializer", KafkaAvroDeserializer.class);
      props.put("schema.registry.url",
          "http://%s:%d".formatted(schemaRegistry.getHost(), schemaRegistry.getMappedPort(8085)));
      props.put(KafkaAvroDeserializerConfig.SPECIFIC_AVRO_READER_CONFIG, "true");
      // configProps.put(KafkaAvroSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
      // TopicRecordNameStrategy.class.getName());
      return new DefaultKafkaConsumerFactory<>(props);
    }

    @Bean
    public ConsumerFactory<String, byte[]> bytesConsumerFactory() {
      var configProps = new HashMap<String, Object>();
      configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG,kafkaContainer.getBootstrapServers());
      // configProps.put("group.id", "byte-group");
      configProps.put("auto.offset.reset", "latest");
      configProps.put("key.deserializer", StringDeserializer.class);
      configProps.put("value.deserializer", ByteArrayDeserializer.class);
      return new DefaultKafkaConsumerFactory<>(configProps);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> stringKafkaListenerContainerFactory() {
      var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
      factory.setConsumerFactory(stringConsumerFactory());
      factory.setConcurrency(1);
      return factory;
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, byte[]> byteKafkaListenerContainerFactory() {
      ConcurrentKafkaListenerContainerFactory<String, byte[]> factory = new ConcurrentKafkaListenerContainerFactory<>();
      factory.setConsumerFactory(bytesConsumerFactory());
      factory.setConcurrency(1);
      return factory;
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, MyMessage> avroKafkaListenerContainerFactory() {
      ConcurrentKafkaListenerContainerFactory<String, MyMessage> factory = new ConcurrentKafkaListenerContainerFactory<>();
      factory.setConsumerFactory(avroConsumerFactory());
      factory.setConcurrency(1);
      return factory;
    }

    @Bean
    public NewTopic newTopic1() {
        return new NewTopic(TEST_TOPIC_STRING, 1, (short) 1);
    }

    @Bean
    public List<NewTopic> newTopics() {
      return List.of(
        new NewTopic(TEST_TOPIC_STRING, 1, (short) 1),
        new NewTopic(TEST_TOPIC_2, 1, (short) 1),
        new NewTopic(TEST_TOPIC_3, 1, (short) 1)
      );
    }

  }
}
