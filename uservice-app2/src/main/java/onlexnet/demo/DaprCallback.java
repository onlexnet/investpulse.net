package onlexnet.demo;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.Empty;

import io.dapr.v1.AppCallbackGrpc.AppCallbackImplBase;
import io.dapr.v1.DaprAppCallbackProtos;
import io.dapr.v1.DaprAppCallbackProtos.ListTopicSubscriptionsResponse;
import io.dapr.v1.DaprAppCallbackProtos.TopicEventRequest;
import io.dapr.v1.DaprAppCallbackProtos.TopicEventResponse;
import io.dapr.v1.DaprAppCallbackProtos.TopicSubscription;
import io.grpc.stub.StreamObserver;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import onlexnet.market.events.MarketChangedEvent;

// source: https://github.com/dapr/java-sdk/blob/master/examples/src/main/java/io/dapr/examples/pubsub/grpc/SubscriberGrpcService.java
/** Entry point of Grpc application services for DAPR */
@Component
@Slf4j
@RequiredArgsConstructor
public class DaprCallback extends AppCallbackImplBase {
    private final ObjectMapper objectMapper;
    
    private final List<TopicSubscription> topicSubscriptionList = new ArrayList<>();
    private final List<EventListener<?>> listeners;

    @PostConstruct
    public void init() {
        log.info("0000000000000000000");
    }

    @Override
    public void listTopicSubscriptions(Empty request, StreamObserver<ListTopicSubscriptionsResponse> responseObserver) {
        log.info("1111111111111");

        for (var l: listeners) {
            var eventClass = l.getEventClass();
            var supportedClassCanonicalName = eventClass.getCanonicalName();
            registerConsumer("pubsub", supportedClassCanonicalName, false);
        }

        registerConsumer("messagebus", "testingtopic", false);
        registerConsumer("messagebus", "bulkpublishtesting", false);
        registerConsumer("messagebus", "testingtopicbulk", true);
        registerConsumer("pubsub", "TOPIC_A", false);
        try {
            var builder = ListTopicSubscriptionsResponse.newBuilder();
            topicSubscriptionList.forEach(builder::addSubscriptions);
            ListTopicSubscriptionsResponse response = builder.build();
            responseObserver.onNext(response);
        } catch (Throwable e) {
            responseObserver.onError(e);
        } finally {
            responseObserver.onCompleted();
        }
    }

    @Override
    @SneakyThrows
    public void onTopicEvent(TopicEventRequest request, StreamObserver<TopicEventResponse> responseObserver) {
        try {
            // dirty deserialization
            // var decoder = MarketChangedEvent.getDecoder();
            var eventAsString = request.getData().toStringUtf8();
            log.info("ON EVENT as string! data={}", eventAsString);
            var payload = objectMapper.readValue(eventAsString, MarketChangedEvent.class);

            log.info("ON EVENT as object: {}", payload);

            var response = DaprAppCallbackProtos.TopicEventResponse.newBuilder()
                    .setStatus(DaprAppCallbackProtos.TopicEventResponse.TopicEventResponseStatus.SUCCESS)
                    .build();
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        } catch (Throwable e) {
            log.error("errrrrrrrrrrrrr", e);
            responseObserver.onError(e);
        }
    }

    /**
     * Add pubsub name and topic to topicSubscriptionList.
     * 
     * @param topic         the topic
     * @param pubsubName    the pubsub name
     * @param isBulkMessage flag to enable/disable bulk subscribe
     */
    public void registerConsumer(String pubsubName, String topic, boolean isBulkMessage) {
        topicSubscriptionList.add(TopicSubscription
                .newBuilder()
                .setPubsubName(pubsubName)
                .setTopic(topic)
                .setBulkSubscribe(DaprAppCallbackProtos.BulkSubscribeConfig.newBuilder().setEnabled(isBulkMessage))
                .build());
    }
}