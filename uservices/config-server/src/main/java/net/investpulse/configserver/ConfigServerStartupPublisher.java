package net.investpulse.configserver;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.cloud.bus.event.RefreshRemoteApplicationEvent;
import org.springframework.cloud.stream.function.StreamBridge;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Component;

/**
 * Publishes a refresh event to Spring Cloud Bus when Config Server starts.
 * This notifies all connected microservices that Config Server is available
 * and they should refresh their configuration.
 * 
 * Services listening to this event will automatically synchronize their config
 * without the need for polling or scheduled retry.
 * 
 * Uses StreamBridge for direct Kafka publishing via Spring Cloud Stream.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ConfigServerStartupPublisher {

    private final StreamBridge streamBridge;

    /**
     * When Config Server is fully started and ready, publish a refresh event
     * to all microservices via Spring Cloud Bus.
     * 
     * Uses StreamBridge to directly publish to Kafka topic.
     */
    @EventListener(ApplicationReadyEvent.class)
    public void publishStartupEvent() {
        log.info("=== ConfigServerStartupPublisher.publishStartupEvent() INVOKED ===");
        log.info("Config Server is ready - publishing refresh event to all services via Spring Cloud Bus");
        
        var refreshEvent = new RefreshRemoteApplicationEvent(
            this,
            "config-server",  // origin service
            "**"              // destination: all services (wildcard pattern)
        );
        
        log.info("Publishing RefreshRemoteApplicationEvent: origin={}, destination={}", 
            refreshEvent.getOriginService(), refreshEvent.getDestinationService());
        
        boolean sent = streamBridge.send("springCloudBus-out-0", 
            MessageBuilder.withPayload(refreshEvent).build());
        
        if (sent) {
            log.info("=== RefreshRemoteApplicationEvent SENT to Kafka topic 'springCloudBus' ===");
        } else {
            log.error("=== FAILED to send RefreshRemoteApplicationEvent to Kafka ===");
        }
    }
}
