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

    private final FinancialSentimentService sentimentService;
    private final KafkaTemplate<String, SentimentResult> kafkaTemplate;

    @KafkaListener(topicPattern = "ticker-.*", groupId = "sentiment-analyzer-group")
    public void processTweet(@Payload RawTweet tweet, 
                             @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
        
        String ticker = topic.replace("ticker-", "");
        log.info("Processing tweet {} for ticker {}", tweet.id(), ticker);

        double score = sentimentService.analyze(tweet.text());
        String label = sentimentService.getSentimentLabel(score);

        SentimentResult result = new SentimentResult(
            tweet.id(),
            ticker,
            score,
            label,
            Instant.now(),
            tweet.publisher(),
            tweet.source()
        );

        kafkaTemplate.send("sentiment-aggregated", ticker, result);
        log.info("Published sentiment result for ticker {}: {}", ticker, label);
    }
}
