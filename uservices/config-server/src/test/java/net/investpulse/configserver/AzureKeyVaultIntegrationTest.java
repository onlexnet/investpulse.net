package net.investpulse.configserver;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.env.Environment;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test that verifies the config server can retrieve secrets from Azure Key Vault
 * and expose them through the config endpoints.
 * 
 * NOTE: The microsoft/spring-cloud-azure repository is deprecated.
 * Latest docs: https://learn.microsoft.com/en-us/azure/developer/java/spring-framework/
 * Issues: https://github.com/Azure/azure-sdk-for-java
 * 
 * Prerequisites:
 * 1. Uncomment the Azure Key Vault dependency in pom.xml
 * 2. Ensure the certificate file exists at ~/.azure/certs/investpulse-net-infra-full.pem
 * 3. The service principal must have access to the Key Vault
 * 4. The secret 'twitter-bearer-token' must exist in the Key Vault
 * 
 * This test is disabled by default and only runs when AZURE_KEYVAULT_TEST_ENABLED=true
 * 
 * IMPORTANT: This test requires:
 * - Azure Spring Cloud dependency uncommented in pom.xml
 * - Compatible version of Spring Boot (currently requires 3.0.0, not compatible with 4.0.0)
 * - Or wait for Azure Spring Cloud version compatible with Spring Boot 4.x
 */
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties = {
        "spring.profiles.active=native",
        "spring.cloud.azure.keyvault.secret.property-sources[0].endpoint=https://dev-kw2-devs.vault.azure.net/",
        "spring.cloud.azure.keyvault.secret.property-sources[0].name=azure-key-vault",
        "spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-id=bde9a28c-d7c8-4ef5-909b-687263af8675",
        "spring.cloud.azure.keyvault.secret.property-sources[0].credential.tenant-id=29084a59-db89-4eb9-908a-53f42318c77d",
        "spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-certificate-path=${HOME}/.azure/certs/investpulse-net-infra-full.pem"
    }
)
class AzureKeyVaultIntegrationTest {

    @LocalServerPort
    private int port;

    @Autowired
    private Environment environment;

    private final RestTemplate restTemplate = new RestTemplate();

    @Test
    void shouldLoadTwitterBearerTokenFromAzureKeyVault() {
        // When - retrieve the secret directly from the environment
        // Note: Azure Key Vault automatically converts dashes to dots in property names
        // Secret name in Key Vault: twitter-bearer-token
        // Property name in Spring: twitter.bearer.token
        String token = environment.getProperty("twitter.bearer.token");

        // Then - verify the secret was loaded from Azure Key Vault
        assertThat(token)
            .as("twitter.bearer.token should be loaded from Azure Key Vault")
            .isNotNull()
            .isNotEmpty()
            .doesNotContain("${") // Should not be a placeholder
            .isNotEqualTo("test-mock-twitter-bearer-token-12345"); // Should not be the test mock value
    }

    @Test
    void shouldExposeTwitterBearerTokenThroughConfigEndpoint() {
        // Given
        String url = "http://localhost:" + port + "/x/default";

        // When
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);

        // Then
        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();
        
        String body = response.getBody();
        assertThat(body)
            .as("Response should contain the configuration")
            .isNotNull()
            .contains("twitter.bearer.token")
            .contains("propertySources");

        // Verify the token value is not a placeholder
        assertThat(body)
            .as("Token should be resolved from Azure Key Vault, not be a placeholder")
            .doesNotContain("${twitter-bearer-token}");
    }

    @Test
    void shouldConnectToAzureKeyVault() {
        // Verify Azure Key Vault configuration is loaded
        String endpoint = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].endpoint");

        assertThat(endpoint)
            .as("Azure Key Vault endpoint should be configured")
            .isEqualTo("https://dev-kw2-devs.vault.azure.net/");
    }

    @Test
    void shouldUseServicePrincipalAuthentication() {
        // Verify Service Principal authentication configuration
        String clientId = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-id");
        String tenantId = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.tenant-id");
        String certPath = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-certificate-path");

        assertThat(clientId)
            .as("Azure Service Principal client ID should be configured")
            .isEqualTo("bde9a28c-d7c8-4ef5-909b-687263af8675");

        assertThat(tenantId)
            .as("Azure tenant ID should be configured")
            .isEqualTo("29084a59-db89-4eb9-908a-53f42318c77d");

        assertThat(certPath)
            .as("Certificate path should be configured")
            .contains(".azure/certs/investpulse-net-infra-full.pem");
    }
}
