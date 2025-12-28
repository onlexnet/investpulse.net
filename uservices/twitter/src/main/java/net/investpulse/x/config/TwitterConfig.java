package net.investpulse.x.config;

import lombok.Data;
import net.investpulse.x.domain.port.TweetFetcher;
import net.investpulse.x.infra.adapter.TwitterApiAdapter;
import net.investpulse.x.infra.interceptor.RateLimitInterceptor;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

import java.util.List;

@Data
@Configuration
@ConfigurationProperties(prefix = "twitter")
public class TwitterConfig {
    private String bearerToken;
    private List<String> accountsToFollow = List.of();
    private int pollIntervalMs = 60000; // Default 1 minute
    private String apiBaseUrl = "https://api.twitter.com/2";

    @Bean
    public RateLimitInterceptor rateLimitInterceptor() {
        return new RateLimitInterceptor();
    }

    @Bean
    public RestClient twitterRestClient(RateLimitInterceptor rateLimitInterceptor) {
        return RestClient.builder()
                .baseUrl(apiBaseUrl)
                .defaultHeader("Authorization", "Bearer " + bearerToken)
                .defaultHeader("Content-Type", "application/json")
                .requestInterceptor(rateLimitInterceptor)
                .build();
    }

    @Bean
    public TweetFetcher tweetFetcher(RestClient twitterRestClient) {
        return new TwitterApiAdapter(twitterRestClient);
    }
}
