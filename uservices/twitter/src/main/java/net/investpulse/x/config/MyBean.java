package net.investpulse.x.config;

import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.EventListener;
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

    @EventListener
    public void handleCustomEvent(ContextRefreshedEvent event) {
        log.warn("Received custom event: {}", event);
    }
}
 