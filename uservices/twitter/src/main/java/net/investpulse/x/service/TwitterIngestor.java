package net.investpulse.x.service;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.investpulse.common.dto.RawTweet;
import net.investpulse.x.config.TwitterConfig;
import net.investpulse.x.domain.port.TweetFetcher;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
@RequiredArgsConstructor
public class TwitterIngestor {

    private final TwitterConfig config;
    private final TweetFetcher tweetFetcher;
    private final DynamicTopicRouter topicRouter;

    // Cache to store the last processed tweet ID per account
    private final Cache<String, String> sinceIdCache = Caffeine.newBuilder()
            .expireAfterWrite(24, TimeUnit.HOURS)
            .build();

    @Scheduled(fixedDelayString = "${twitter.poll-interval-ms:60000}")
    public void pollTweets() {
        log.info("Starting tweet poll for {} accounts", config.getAccountsToFollow().size());

        for (String account : config.getAccountsToFollow()) {
            try {
                String sinceId = sinceIdCache.getIfPresent(account);
                List<RawTweet> tweets = tweetFetcher.fetchTweets(account, sinceId);

                for (RawTweet tweet : tweets) {
                    topicRouter.route(tweet);
                    sinceIdCache.put(account, tweet.id());
                }

                log.info("Processed {} tweets for account {}", tweets.size(), account);
            } catch (Exception e) {
                log.error("Error polling tweets for account {}: {}", account, e.getMessage());
            }
        }
    }
}
