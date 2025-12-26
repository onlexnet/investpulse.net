package net.investpulse.x.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Data
@Configuration
@ConfigurationProperties(prefix = "twitter")
public class TwitterConfig {
    private String bearerToken;
    private List<String> accountsToFollow = List.of();
    private int pollIntervalMs = 60000; // Default 1 minute
}
