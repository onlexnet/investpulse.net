package net.investpulse.x.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@RequiredArgsConstructor
public class DynamicTopicRouter {

    private final KafkaTemplate<String, RawTweet> kafkaTemplate;
    private final KafkaAdmin kafkaAdmin;
    private final Set<String> existingTopics = ConcurrentHashMap.newKeySet();

    public void route(RawTweet tweet) {
        if (tweet.tickers() == null || tweet.tickers().isEmpty()) {
            log.debug("No tickers found in tweet {}, skipping routing", tweet.id());
            return;
        }

        for (String ticker : tweet.tickers()) {
            String topicName = "ticker-" + ticker.toUpperCase();
            ensureTopicExists(topicName);
            kafkaTemplate.send(topicName, ticker, tweet);
            log.info("Routed tweet {} to topic {}", tweet.id(), topicName);
        }
    }

    private void ensureTopicExists(String topicName) {
        if (!existingTopics.contains(topicName)) {
            log.info("Creating dynamic topic: {}", topicName);
            NewTopic newTopic = new NewTopic(topicName, 1, (short) 1);
            kafkaAdmin.createOrModifyTopics(newTopic);
            existingTopics.add(topicName);
        }
    }
}
