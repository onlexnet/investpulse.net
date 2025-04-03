package onlexnet.webapi.events;

import org.jmolecules.event.annotation.DomainEvent;

public interface NewTickersDiscovered {

  @DomainEvent
  record Event(Ticker[] tickers) { }

  record Ticker(String ticker) { }

}
