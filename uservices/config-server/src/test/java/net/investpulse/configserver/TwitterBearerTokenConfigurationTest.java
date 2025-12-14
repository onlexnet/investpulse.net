package net.investpulse.configserver;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Test verifying that the config server properly exposes the twitter-bearer-token secret
 * from the configuration files.
 */
class TwitterBearerTokenConfigurationTest {

    @Test
    void xPropertiesFileShouldContainTwitterBearerTokenPlaceholder() throws IOException {
        // Given
        Path xPropertiesPath = Path.of("src/main/resources/config/x.properties");

        // When
        String content = Files.readString(xPropertiesPath);

        // Then
        assertThat(content)
            .as("x.properties should contain twitter bearer token configuration")
            .contains("twitter.bearer.token");
        
        // The value should be a placeholder that will be overridden by Config Server
        // from Azure Key Vault using spring.cloud.config.server.overrides
    }

    @Test
    void applicationPropertiesShouldConfigureAzureKeyVault() throws IOException {
        // Given
        Path appPropertiesPath = Path.of("src/main/resources/application.properties");

        // When
        String content = Files.readString(appPropertiesPath);

        // Then
        assertThat(content)
            .as("application.properties should contain Azure Key Vault configuration")
            .contains("spring.cloud.azure.keyvault.secret.property-sources[0].endpoint=https://dev-kw2-devs.vault.azure.net/")
            .contains("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-id=bde9a28c-d7c8-4ef5-909b-687263af8675")
            .contains("spring.cloud.azure.keyvault.secret.property-sources[0].credential.tenant-id=29084a59-db89-4eb9-908a-53f42318c77d")
            .contains("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-certificate-path");
    }

    @Test
    void testPropertiesShouldContainMockTwitterBearerToken() throws IOException {
        // Given
        Path testPropertiesPath = Path.of("src/test/resources/application.properties");

        // When
        String content = Files.readString(testPropertiesPath);

        // Then
        assertThat(content)
            .as("test application.properties should contain mock twitter bearer token")
            .contains("twitter-bearer-token=test-mock-twitter-bearer-token-12345");
    }
}
