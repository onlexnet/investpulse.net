package onlexnet.webapi.api;

import java.time.Duration;
import java.time.LocalDateTime;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import onlexnet.webapi.avro.MyMessage;
import reactor.core.Disposable;
import reactor.core.Disposables;
import reactor.core.publisher.Flux;

@RequiredArgsConstructor
@Component
final class TimerPublisher implements AutoCloseable {
    
    private final KafkaTemplate<String, MyMessage> kafkaTemplate;
    private final Disposable.Composite disposer = Disposables.composite();

    @PostConstruct
    public void init() {
        var timerDisposer = Flux.interval(Duration.ofSeconds(1)).map(t -> LocalDateTime.now())
            .subscribe(it -> {
                var now = LocalDateTime.now();
                var event = TimeEvent.of(now);
                kafkaTemplate.send("timer-topic-1", event);
            });
        disposer.add(timerDisposer);
    }

    @Override
    public void close() {
        disposer.dispose();
    }

    
}
