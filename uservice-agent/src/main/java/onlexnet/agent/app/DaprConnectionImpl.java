package onlexnet.agent.app;

import java.util.List;

import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import io.dapr.client.DaprPreviewClient;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;

@Component
@RequiredArgsConstructor
class DaprConnectionImpl implements DaprConnection, AutoCloseable {

  private final ObjectMapper objectMapper;

  private DaprPreviewClient client;

  @PostConstruct
  void init() {
    client = new DaprClientBuilder()
        .buildPreviewClient();
  }

  @Override
  public void close() throws Exception {
    client.close();
  }

  @Override
  @SneakyThrows
  public <T> void publish(T event) {
    var topicName = onlexnet.pdt.Topics.asTopicName(event);

    var body = objectMapper.writeValueAsString(event);

    // interesting observation: if contentType is application/json, it adds at
    // deserializatrion stage at dapr level additional quotes and the beginning
    // and the end of message, so deserialization fails.
    // using text/plain make it working
    var callResult = client.publishEvents("pubsub", topicName, "text/plain", List.of(body));
    callResult.block();
  }

}
