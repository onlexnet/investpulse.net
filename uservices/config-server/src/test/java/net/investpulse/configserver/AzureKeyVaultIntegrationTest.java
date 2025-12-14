package net.investpulse.configserver;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.env.Environment;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test verifying Config Server retrieves secrets from Azure Key Vault
 * and exposes them through config endpoints.
 *
 * <p>Azure Key Vault automatically converts dashes to dots in property names:
 * <ul>
 *   <li>Secret name in Key Vault: {@code twitter-bearer-token}</li>
 *   <li>Property name in Spring: {@code twitter.bearer.token}</li>
 * </ul>
 *
 * <p>Prerequisites:
 * <ul>
 *   <li>Certificate file: {@code ~/.azure/certs/investpulse-net-infra-full.pem}</li>
 *   <li>Service Principal has Key Vault access</li>
 *   <li>Secret {@code twitter-bearer-token} exists in Key Vault</li>
 * </ul>
 *
 * @see <a href="https://learn.microsoft.com/en-us/azure/developer/java/spring-framework/">Azure Spring Documentation</a>
 */
@ActiveProfiles("native")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AzureKeyVaultIntegrationTest {

    private static final String AZURE_KEY_VAULT_ENDPOINT = "https://dev-kw2-devs.vault.azure.net/";
    private static final String SERVICE_PRINCIPAL_CLIENT_ID = "bde9a28c-d7c8-4ef5-909b-687263af8675";
    private static final String SERVICE_PRINCIPAL_TENANT_ID = "29084a59-db89-4eb9-908a-53f42318c77d";
    private static final String CERTIFICATE_FILENAME = "investpulse-net-infra-full.pem";
    private static final String MOCK_TOKEN = "test-mock-twitter-bearer-token-12345";

    @LocalServerPort
    private int port;

    @Autowired
    private Environment environment;

    private final RestTemplate restTemplate = new RestTemplate();

    @Test
    void shouldLoadTwitterBearerTokenFromAzureKeyVault() {
        var token = environment.getProperty("twitter.bearer.token");

        assertThat(token)
            .as("twitter.bearer.token should be loaded from Azure Key Vault")
            .isNotNull()
            .isNotEmpty()
            .doesNotContain("${")
            .isNotEqualTo(MOCK_TOKEN);
    }

    @Test
    void shouldExposeTwitterBearerTokenThroughConfigEndpoint() {
        var url = "http://localhost:" + port + "/x/default";
        var response = restTemplate.getForEntity(url, String.class);

        assertThat(response.getStatusCode().is2xxSuccessful()).isTrue();

        var body = response.getBody();
        assertThat(body)
            .as("Response should contain the configuration")
            .isNotNull()
            .contains("twitter.bearer.token", "propertySources")
            .as("Token should be resolved from Azure Key Vault, not be a placeholder")
            .doesNotContain("${twitter-bearer-token}");
    }

    @Test
    void shouldConnectToAzureKeyVault() {
        var endpoint = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].endpoint");

        assertThat(endpoint)
            .as("Azure Key Vault endpoint should be configured")
            .isEqualTo(AZURE_KEY_VAULT_ENDPOINT);
    }

    @Test
    void shouldUseServicePrincipalAuthentication() {
        var clientId = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-id");
        var tenantId = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.tenant-id");
        var certPath = environment.getProperty("spring.cloud.azure.keyvault.secret.property-sources[0].credential.client-certificate-path");

        assertThat(clientId)
            .as("Azure Service Principal client ID should be configured")
            .isEqualTo(SERVICE_PRINCIPAL_CLIENT_ID);

        assertThat(tenantId)
            .as("Azure tenant ID should be configured")
            .isEqualTo(SERVICE_PRINCIPAL_TENANT_ID);

        assertThat(certPath)
            .as("Certificate path should be configured")
            .contains(CERTIFICATE_FILENAME);
    }
}
