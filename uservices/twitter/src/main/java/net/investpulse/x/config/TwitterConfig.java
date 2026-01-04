package net.investpulse.x.config;

import net.investpulse.x.domain.port.TweetFetcher;
import net.investpulse.x.infra.adapter.TwitterApiAdapter;
import net.investpulse.x.infra.interceptor.RateLimitInterceptor;

import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.ScopedProxyMode;
import org.springframework.web.client.RestClient;

import lombok.extern.slf4j.Slf4j;

@Configuration
@Slf4j
public class TwitterConfig {

    @Bean
    @RefreshScope(proxyMode = ScopedProxyMode.NO) // to avoid create proxy by Spring for final TwitterProps.Configuration
    public TwitterProps.Configuration twitterPropsConfiguration(TwitterRawProps rawProps) {
        log.info("TwitterProps.Configuration initialized with accountsToFollow: {}", rawProps.getAccountsToFollow());
        return new TwitterProps.Configuration(
                rawProps.getBearerToken(),
                rawProps.getAccountsToFollow(),
                rawProps.getPollIntervalMs(),
                rawProps.getApiBaseUrl()
        );
    }

    @Bean
    public RateLimitInterceptor rateLimitInterceptor() {
        return new RateLimitInterceptor();
    }

    @Bean
    @RefreshScope
    public RestClient twitterRestClient(RateLimitInterceptor rateLimitInterceptor, TwitterProps.Configuration twitterProps) {
        return RestClient.builder()
                .baseUrl(twitterProps.apiBaseUrl())
                .defaultHeader("Authorization", "Bearer " + twitterProps.bearerToken())
                .defaultHeader("Content-Type", "application/json")
                .requestInterceptor(rateLimitInterceptor)
                .build();
    }

    @Bean
    @RefreshScope
    public TweetFetcher tweetFetcher(RestClient twitterRestClient) {
        return new TwitterApiAdapter(twitterRestClient);
    }
}
