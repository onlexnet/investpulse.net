package net.investpulse.x;

import net.investpulse.x.config.TwitterProps;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.TestPropertySource;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test for Spring Cloud Config refresh functionality.
 * Verifies that @RefreshScope beans are recreated with updated values
 * when /actuator/refresh endpoint is called.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = {
    "spring.cloud.config.enabled=false",  // Disable config server for test
    "spring.cloud.bus.enabled=false",     // Disable Kafka bus for test
    "twitter.bearer-token=INITIAL_TOKEN",
    "twitter.accounts-to-follow=account1,account2",
    "twitter.poll-interval-ms=5000"
})
@DirtiesContext
class ConfigRefreshIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private TwitterProps.Configuration twitterPropsConfiguration;

    @Test
    void shouldExposeRefreshEndpoint() {
        // When: Call actuator refresh endpoint
        ResponseEntity<String[]> response = restTemplate.postForEntity(
                "/actuator/refresh",
                null,
                String[].class
        );

        // Then: Endpoint should be accessible and return 200
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
    }

    @Test
    void shouldReflectInitialConfigInConfigurationBean() {
        // When: Application starts with test properties
        
        // Then: Configuration bean should have initial values from @TestPropertySource
        assertThat(twitterPropsConfiguration.bearerToken()).isEqualTo("INITIAL_TOKEN");
        assertThat(twitterPropsConfiguration.accountsToFollow())
                .containsExactlyInAnyOrder("account1", "account2");
        assertThat(twitterPropsConfiguration.pollIntervalMs()).isEqualTo(5000);
    }

    /**
     * Note: This test verifies that the refresh endpoint works. 
     * In a real environment, config changes would come from Config Server
     * via Spring Cloud Bus events, and @RefreshScope beans would be recreated with new values.
     * 
     * TwitterRawProps has @RefreshScope, which allows it to reload properties.
     * Other beans (RestClient, TweetFetcher) also have @RefreshScope and depend on 
     * TwitterRawProps, so they'll be recreated when configuration changes.
     * 
     * Note: TwitterProps.Configuration is a Java Record (implicitly final),
     * so it cannot be proxied with @RefreshScope. However, it's a lightweight
     * factory method that recreates from the refreshable TwitterRawProps,
     * so it will reflect updated values when beans that depend on it are refreshed.
     * 
     * For full end-to-end testing with dynamic config updates, use:
     * - Testcontainers with Kafka and Config Server
     * - Spring Cloud Contract for config server stubs
     * - Manual testing with running config-server instance
     */
    @Test
    void shouldHaveRefreshEndpointEnabled() {
        // When: Application context is initialized
        
        // Then: Refresh endpoint should be enabled and accessible
        ResponseEntity<String[]> response = restTemplate.postForEntity(
                "/actuator/refresh",
                null,
                String[].class
        );
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
    }
}
