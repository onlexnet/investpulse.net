package net.investpulse.x.config;

import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.bus.event.RefreshRemoteApplicationEvent;
import org.springframework.cloud.context.refresh.ContextRefresher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;

/**
 * Listens for Spring Cloud Bus events from Config Server.
 * When Config Server publishes a refresh event (e.g., when it starts or config changes),
 * this listener automatically picks up the new configuration without polling or retry.
 * 
 * This is an event-driven approach that eliminates the need for scheduled retry.
 */
@Slf4j
@Component
public class ConfigServerEventListener {

    @Autowired
    ContextRefresher refresher;

    @Autowired
    TwitterRawProps twitterRawProps;

    @PostConstruct
    void init() {
        var accounts = twitterRawProps.getAccountsToFollow();
        log.info("ConfigServerEventListener initialized with accounts: {}", accounts);
    }
    /**
     * Handles refresh events from Config Server via Spring Cloud Bus (Kafka).
     * Automatically triggered when:
     * 1. Config Server starts up and publishes its availability
     * 2. Configuration changes and Config Server publishes refresh event
     * 3. Manual refresh is triggered via /actuator/busrefresh
     */
    @EventListener
    public void handleRefreshEvent(RefreshRemoteApplicationEvent event) {
        log.info("Received refresh event from {}", event.getOriginService());
        var aaa1 = twitterRawProps.getAccountsToFollow();
        refresher.refresh();  // <- to triggeruje @RefreshScope
        var aaa2 = twitterRawProps.getAccountsToFollow();
        log.info("Refreshed TwitterRawProps accounts from {} to {}", aaa1, aaa2);
        // TODO - should we send back AckRemoteApplicationEvent?
    }
}
