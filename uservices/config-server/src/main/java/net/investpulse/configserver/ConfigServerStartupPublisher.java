package net.investpulse.configserver;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cloud.bus.event.RefreshRemoteApplicationEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * Publishes a refresh event to Spring Cloud Bus when Config Server starts.
 * This notifies all connected microservices that Config Server is available
 * and they should refresh their configuration.
 * 
 * Services listening to this event will automatically synchronize their config
 * without the need for polling or scheduled retry.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ConfigServerStartupPublisher {

    private final ApplicationEventPublisher eventPublisher;

    /**
     * When Config Server is fully started and ready, publish a refresh event
     * to all microservices via Kafka (Spring Cloud Bus).
     */
    @EventListener(ApplicationReadyEvent.class)
    public void publishStartupEvent() {
        log.info("Config Server is ready - publishing refresh event to all services");
        
        var refreshEvent = new RefreshRemoteApplicationEvent(
            this,
            "config-server",  // origin service
            "**"              // destination: all services (use ** for wildcard)
        );
        
        eventPublisher.publishEvent(refreshEvent);
        log.info("Config Server availability event published to Spring Cloud Bus");
    }
}
