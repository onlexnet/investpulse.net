package net.investpulse.x.config;

import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;

import lombok.Data;

public sealed interface TwitterProps {

    record Configuration(String bearerToken,
            Iterable<String> accountsToFollow,
            int pollIntervalMs,
            String apiBaseUrl) implements TwitterProps { }

    /** Configuration is not yet available. */
    enum Waiting implements TwitterProps {
        INSTANCE
    }

    /**
     * We have invalid properties, so components depending on TwitterProps should not function
     */
    enum InvalidProps implements TwitterProps {
        INSTANCE
    }

}

@ConfigurationProperties(prefix = "twitter")
@Data
class TwitterRawProps {
    private String bearerToken;
    private List<String> accountsToFollow = List.of();
    private int pollIntervalMs = 1000; // Default 1 second for testing
    private String apiBaseUrl = "https://api.twitter.com/2";
}
