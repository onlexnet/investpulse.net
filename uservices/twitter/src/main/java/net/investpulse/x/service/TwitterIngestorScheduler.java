package net.investpulse.x.service;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class TwitterIngestorScheduler {

    private final TwitterIngestor twitterIngestor;

    // @Scheduled(fixedDelayString = "${twitter.poll-interval-ms:60000}")
    @Scheduled(fixedDelay = 3_000)
    public void pollTweets() {
        twitterIngestor.pollTweets();
    }
}
