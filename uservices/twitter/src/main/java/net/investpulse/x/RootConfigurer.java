package net.investpulse.x;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.MessagePublisher;
import net.investpulse.x.infra.adapter.KafkaMessagePublisher;

@SpringBootApplication
@EnableScheduling
@ConfigurationPropertiesScan
class RootConfigurer {
    
    @Bean
    MessagePublisher messagePublisher(
            KafkaTemplate<String, RawTweet> kafkaTemplate,
            KafkaAdmin kafkaAdmin) {
        return new KafkaMessagePublisher(kafkaTemplate, kafkaAdmin);
    }
}
