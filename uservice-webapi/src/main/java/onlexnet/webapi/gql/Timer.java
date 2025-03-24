package onlexnet.webapi.gql;

import java.time.Duration;
import java.time.LocalDateTime;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.reactivestreams.Publisher;
import org.springframework.kafka.annotation.KafkaListener;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsSubscription;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import onlexnet.webapi.api.TimeEvent;
import onlexnet.webapi.avro.MyMessage;
import reactor.core.publisher.Flux;
import reactor.core.publisher.FluxSink;
import reactor.core.publisher.FluxSink.OverflowStrategy;

@DgsComponent
@Slf4j
public class Timer {

  FluxSink<MyMessage> proxy;
  Flux<MyMessage> listener;

  @PostConstruct
  void init() {
    listener = Flux.<MyMessage>create(it -> this.proxy = it, OverflowStrategy.BUFFER);
    listener.subscribe();
    log.error("SPARTAAAAAAAAAAAAA {}", proxy);
  }

  @KafkaListener(topics = "timer-topic-1")
  public void onEvent(ConsumerRecord<String, MyMessage> eventRecord) {
    var event = eventRecord.value();
    proxy.next(event);
  }

  @DgsSubscription
  public Publisher<LocalDateTime> timer() {
      return listener.map(it -> TimeEvent.of(it));
  }
}

