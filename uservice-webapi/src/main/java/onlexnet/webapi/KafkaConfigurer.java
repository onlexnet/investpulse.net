package onlexnet.webapi;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;

import io.confluent.kafka.serializers.KafkaAvroSerializer;
import onlexnet.webapi.avro.MyMessage;

// @Configuration
class KafkaProducerConfig {

    private final String bootstrapServers = "localhost:9092";

    private Map<String, Object> producerConfigs(Class<?> valueSerializer) {
        Map<String, Object> props = new HashMap<>();
        // props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, valueSerializer);
        return props;
    }

    @Bean
    public ProducerFactory<String, String> stringProducerFactory() {
        return new DefaultKafkaProducerFactory<>(producerConfigs(StringSerializer.class));
    }

    @Bean
    public KafkaTemplate<String, String> stringKafkaTemplate() {
        return new KafkaTemplate<>(stringProducerFactory());
    }

    @Bean
    public KafkaTemplate<String, MyMessage> integerKafkaTemplate() {
        return new KafkaTemplate<>(customObjectProducerFactory());
    }

    @Bean
    public ProducerFactory<String, MyMessage> customObjectProducerFactory() {
        return new DefaultKafkaProducerFactory<>(producerConfigs(KafkaAvroSerializer.class));
    }

}
