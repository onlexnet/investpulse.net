package onlexnet.webapi;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.Queue;
import java.util.UUID;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
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
import org.springframework.kafka.listener.ConcurrentMessageListenerContainer;
import org.springframework.kafka.listener.MessageListener;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.test.context.ActiveProfiles;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@SpringBootTest(webEnvironment = WebEnvironment.NONE)
@Import({ KafkaIntegrationTest.MyConsumer.class, KafkaIntegrationTest.LocalConfiguration.class })
@ActiveProfiles("test")
@Slf4j
@EnableKafka
public class KafkaIntegrationTest {

    static final String TEST_TOPIC = "my-topic-2";
    static final String BOOTSTRAP_SERVER = "localhost:9094";

    @Autowired
    KafkaTemplate<String, String> kafkaTemplate;

    @Autowired
    BlockingQueue<String> messages;

    @Test
    void shouldSendAndReceiveMessage() throws InterruptedException, ExecutionException {
        var value = "value: " + LocalDateTime.now();
        var r = kafkaTemplate.send(TEST_TOPIC, UUID.randomUUID().toString(), value).get();
        kafkaTemplate.flush();

        var received = messages.poll(11, TimeUnit.SECONDS);
        Assertions.assertThat(received).isEqualTo(value);
    }

    @RequiredArgsConstructor
    @Component
    static class MyConsumer {

        private final BlockingQueue<String> messages;

        @KafkaListener(id = "MyConsumerrrrrrrrrrrrrrrrrrrrrr", topics = KafkaIntegrationTest.TEST_TOPIC)
        public void accept(String t) throws InterruptedException {
            messages.put(t);
        }

    }

    @Configuration
    @EnableKafka
    static class LocalConfiguration {

        @Bean
        public BlockingQueue<String> messages() {
            return new LinkedBlockingQueue<String>();
        }

        @Bean
        public ProducerFactory<String, String> producerFactory() {
            var configProps = new HashMap<String, Object>();
            configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVER);
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
            var props = new HashMap<String, Object>();
            props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVER);
            props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group-4");
            props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
            props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
            props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
            var result = new DefaultKafkaConsumerFactory<String, String>(props);
            result.addListener(new ConsumerFactory.Listener<String, String>() {
		        public void consumerAdded(@NonNull String id, @NonNull Consumer<String, String> consumer) {
                    log.info("11111111");
		        }

        		public void consumerRemoved(@NonNull String id, @NonNull Consumer<String, String> consumer) {
                    log.info("222222222");
		        }
            });
            return result;
        }

        @Bean
        public ConcurrentMessageListenerContainer<String, String> kafkaMessageListenerContainer(ConcurrentKafkaListenerContainerFactory<String, String> factory) {
            var container = factory.createContainer(TEST_TOPIC);
            container.setupMessageListener(new MessageListener<String, String>() {

                @Override
                public void onMessage(@NonNull ConsumerRecord<String, String> data) {
                    log.info("SPARTAAAAAAAAAAAAAAAAAAAAAAA" + data);
                }
                
            });
            return container;
        }

        @Bean
        public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(ConsumerFactory<String, String> consumerFactory) { 
            var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
            factory.setConsumerFactory(consumerFactory);
            var props = factory.getContainerProperties();
            return factory;
        }

        @KafkaListener(id = "aaaaaaaaaaaaaa", topics = KafkaIntegrationTest.TEST_TOPIC, groupId = "asdasdsadas")
        public void accept(String t) {
            log.info("SPARTAAAAAAAAAAAA2222222222222222");
        }
    }
}
