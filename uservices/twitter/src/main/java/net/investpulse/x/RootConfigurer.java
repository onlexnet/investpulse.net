package net.investpulse.x;

import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.domain.port.MessagePublisher;
import net.investpulse.x.infra.adapter.KafkaMessagePublisher;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
class RootConfigurer {
    
    @Bean
    MessagePublisher messagePublisher(
            KafkaTemplate<String, RawTweet> kafkaTemplate,
            KafkaAdmin kafkaAdmin) {
        return new KafkaMessagePublisher(kafkaTemplate, kafkaAdmin);
    }
}
