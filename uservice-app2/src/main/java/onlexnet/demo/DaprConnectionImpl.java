package onlexnet.demo;

import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
class DaprConnectionImpl implements DaprConnection, AutoCloseable {
  
  private DaprClient client;

  @PostConstruct
  void init() {
    client = new DaprClientBuilder()
        .build();
        client.waitForSidecar(10_000);
    log.info("?????????????????????????????");
  }

  // @EventListener
  // public void onEvent(PublishEventRequest event) {
  //   client.publishEvent(event);
  // }

  @Override
  public void close() throws Exception {
    client.close();
  }

}
