package onlexnet.webapi.gql;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.concurrent.atomic.AtomicInteger;

import org.reactivestreams.Publisher;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsSubscription;

import reactor.core.publisher.Flux;

@DgsComponent
public class Timer {

    AtomicInteger a = new AtomicInteger();

    @DgsSubscription
    public Publisher<String> timer() {
        return Flux.interval(Duration.ofSeconds(1)).map(t -> LocalDateTime.now().toString());
    }
}

