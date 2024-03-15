package onlexnet.demo;

import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import onlexnet.market.events.MarketChangedEvent;

@Component
@Slf4j
public class MarketChangedEventListener implements EventListener<MarketChangedEvent> {

    @Override
    public Class<MarketChangedEvent> getEventClass() {
        return MarketChangedEvent.class;
    }

    @Override
    public void onEvent(MarketChangedEvent event) {
        log.info("On event: {}", event);
    }

}
