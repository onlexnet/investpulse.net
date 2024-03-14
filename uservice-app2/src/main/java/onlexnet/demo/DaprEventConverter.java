package onlexnet.demo;

import java.io.ByteArrayOutputStream;

import org.apache.avro.io.EncoderFactory;
import org.apache.avro.specific.SpecificDatumWriter;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import io.dapr.client.domain.PublishEventRequest;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import onlexnet.market.events.MarketChangedEvent;

@Component
@Slf4j
class DaprEventConverter {
  
  @SneakyThrows
  @EventListener
  // public PublishEventRequest on(onlexnet.market.events.MarketChangedEvent event) {
  public void on(onlexnet.market.events.MarketChangedEvent event) {
    final var wr = new SpecificDatumWriter<>(MarketChangedEvent.class);
    var stream = new ByteArrayOutputStream();
    var encoder = EncoderFactory.get().jsonEncoder(MarketChangedEvent.SCHEMA$, stream);
    wr.write(event, encoder);
    encoder.flush();
    var data = stream.toByteArray();

    log.info("EVENT! %s", event);

    // return new PublishEventRequest("pubsub", "MYTOPICNAME", data);
  }

}
