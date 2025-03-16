package onlexnet.webapi.gql;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;

import org.reactivestreams.Publisher;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsSubscription;

import reactor.core.publisher.Flux;

@DgsComponent
public class Timer {

    AtomicInteger a = new AtomicInteger();

    @DgsSubscription
    public Publisher<Stock> stocks() {
        return Flux.interval(Duration.ofSeconds(1)).map(t -> new Stock("NFLX", 500 + a.incrementAndGet()));
    }
}

record Stock(String name, int value) { }