package net.investpulse.x.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.kafka.support.KafkaUtils;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
public class MyBean {
    
    @PostConstruct
    void init() {
        log.warn("MyBean has been initialized");
    }

    @Value("${spring.kafka.consumer.group-id:default-group}")
    private String consumerGroupId;
    
    @EventListener
    public void handleCustomEvent(ContextRefreshedEvent event) {
        log.warn("Received custom event: {}", event);
        var groupId = KafkaUtils.getConsumerGroupId();
        log.warn("Kafka Consumer Group ID: {}", groupId);

    }
}
 