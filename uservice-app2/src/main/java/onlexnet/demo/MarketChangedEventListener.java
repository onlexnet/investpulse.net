package onlexnet.demo;

import org.springframework.stereotype.Component;

import onlexnet.market.events.MarketChangedEvent;

@Component
public class MarketChangedEventListener implements EventListener<MarketChangedEvent> {

    @Override
    public Class<MarketChangedEvent> getEventClass() {
        return MarketChangedEvent.class;
    }

    @Override
    public void onEvent(MarketChangedEvent event) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'onEvent'");
    }
    
}
