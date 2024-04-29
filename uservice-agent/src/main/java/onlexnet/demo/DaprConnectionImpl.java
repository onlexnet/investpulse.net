package onlexnet.demo;

import org.springframework.stereotype.Component;

import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import jakarta.annotation.PostConstruct;

@Component
class DaprConnectionImpl implements DaprConnection, AutoCloseable {
  
  private DaprClient client;

  @PostConstruct
  void init() {
    client = new DaprClientBuilder()
        .build();
        client.waitForSidecar(10_000);
  }

  @Override
  public void close() throws Exception {
    client.close();
  }

}
