package net.investpulse.sentiment.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.common.dto.SentimentResult;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Slf4j
@Service
@RequiredArgsConstructor
public class SentimentAggregator {

    private static final String TOPIC_PREFIX = "ticker-";
    private static final String OUTPUT_TOPIC = "sentiment-aggregated";
    private static final String EMPTY_STRING = "";

    private final FinancialSentimentService sentimentService;
    private final KafkaTemplate<String, SentimentResult> kafkaTemplate;

    @KafkaListener(topicPattern = "ticker-.*", groupId = "sentiment-analyzer-group")
    public void processTweet(@Payload RawTweet tweet, 
                             @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        
        var ticker = topic.replace(TOPIC_PREFIX, EMPTY_STRING);
        log.info("Processing tweet {} for ticker {}", tweet.id(), ticker);

        var score = sentimentService.analyze(tweet.text());
        var label = sentimentService.getSentimentLabel(score);

        var result = new SentimentResult(
            tweet.id(),
            ticker,
            score,
            label,
            Instant.now(),
            tweet.publisher(),
            tweet.source()
        );

        kafkaTemplate.send(OUTPUT_TOPIC, ticker, result);
        log.info("Published sentiment result for ticker {}: {}", ticker, label);
    }
}
