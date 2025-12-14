# Config Server - Azure Key Vault Integration

## Overview

This config server is prepared to integrate with Azure Key Vault for secure secret management. The configuration for accessing secrets from `https://dev-kw2-devs.vault.azure.net/` is already in place in `application.properties`.

## Configuration

The following Azure Key Vault configuration is set in `src/main/resources/application.properties`:

```properties
# Azure Key Vault configuration
spring.cloud.azure.keyvault.secret.endpoint=https://dev-kw2-devs.vault.azure.net/
spring.cloud.azure.keyvault.secret.property-source-enabled=true

# Azure Service Principal Certificate-Based Authentication
spring.cloud.azure.credential.client-id=bde9a28c-d7c8-4ef5-909b-687263af8675
spring.cloud.azure.credential.tenant-id=29084a59-db89-4eb9-908a-53f42318c77d
spring.cloud.azure.credential.client-certificate-path=${HOME}/.azure/certs/investpulse-net-infra-full.pem
```

## Twitter Bearer Token Secret

The config server exposes the `twitter-bearer-token` secret from Azure Key Vault through the `x.properties` file:

**File**: `src/main/resources/config/x.properties`
```properties
twitter.bearer.token=${twitter-bearer-token}
```

## Azure Dependency

**IMPORTANT**: Azure Key Vault Spring Boot starter is currently **NOT compatible with Spring Boot 4.0.0**.

### Deprecation Notice

⚠️ **The `microsoft/spring-cloud-azure` repository is deprecated.**

For the latest Azure Spring Cloud documentation and issues:
- **Documentation**: [Microsoft Docs - Spring Cloud Azure](https://learn.microsoft.com/en-us/azure/developer/java/spring-framework/)
- **Issues & Support**: [Azure SDK for Java repo](https://github.com/Azure/azure-sdk-for-java)
- **Maven Artifacts**: `com.azure.spring:spring-cloud-azure-*`

### Compatibility Issue

The Azure Spring Cloud library explicitly checks version compatibility and **requires Spring Boot 3.0.0**:

```
Spring Boot [4.0.0] is not compatible with this Spring Cloud Azure version.
Change Spring Boot version to one of the following versions [3.0.0].
```

Additionally, Azure Spring Cloud 5.18.0 uses classes that were removed in Spring Boot 4.0.0:
```
java.lang.NoClassDefFoundError: org/springframework/boot/ConfigurableBootstrapContext
```

### Tested Versions

| Azure Spring Cloud | Spring Boot | Status |
|-------------------|-------------|---------|
| 5.18.0 | 4.0.0 | ❌ Missing classes (`ConfigurableBootstrapContext`) |
| 6.0.0-beta.4 | 4.0.0 | ❌ Official incompatibility check fails |
| 5.18.0 / 6.0.0-beta.4 | 3.0.0 | ✅ Compatible |

### Current Status

The dependency is **commented out** in `pom.xml`:

```xml
<!-- Azure Key Vault integration - NOT compatible with Spring Boot 4.0.0
     Latest Azure Spring Cloud (6.0.0-beta.4) requires Spring Boot 3.0.0
     Uncomment when compatible version is released for Spring Boot 4.x
<dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-starter-keyvault-secrets</artifactId>
</dependency>
-->
```

### Options to Enable Azure Key Vault

**Option 1**: Downgrade to Spring Boot 3.0.0
- Change `<version>4.0.0</version>` to `<version>3.0.0</version>` in parent POM
- Uncomment the Azure dependency
- Use `spring-cloud-azure.version=5.18.0` or `6.0.0-beta.4`

**Option 2**: Wait for Azure Spring Cloud compatible with Spring Boot 4.x
- Monitor [Azure SDK for Java releases](https://github.com/Azure/azure-sdk-for-java/releases)
- Check compatibility matrix at [Microsoft Docs](https://learn.microsoft.com/en-us/azure/developer/java/spring-framework/spring-versions-support-policy)

**Option 3**: Implement custom Azure Key Vault client
- Use Azure SDK directly without Spring Boot integration
- Add dependency: `com.azure:azure-security-keyvault-secrets`
- More control but requires more code
```

## Authentication

The config server uses certificate-based authentication with Azure Service Principal. For details about the authentication setup, see `../AZURE-AUTH-README.md`.

### Required Certificate

Ensure the certificate file is available at:
```
~/.azure/certs/investpulse-net-infra-full.pem
```

### Service Principal Details

- **Application ID**: `bde9a28c-d7c8-4ef5-909b-687263af8675`
- **Tenant ID**: `29084a59-db89-4eb9-908a-53f42318c77d`
- **Key Vault**: `https://dev-kw2-devs.vault.azure.net/`

## Testing

The project includes tests that verify the configuration:

### Unit Tests

- `TwitterBearerTokenConfigurationTest` - Verifies that:
  - `x.properties` contains the twitter bearer token placeholder
  - `application.properties` contains Azure Key Vault configuration
  - Test properties contain a mock twitter bearer token for testing

Run unit tests with:
```bash
mvn test
```

### Integration Test with Azure Key Vault

- `AzureKeyVaultIntegrationTest` - **Real integration test** that:
  - Starts the config server with Azure Key Vault connection
  - Retrieves the actual `twitter-bearer-token` secret from Azure Key Vault
  - Verifies the secret is exposed through the config endpoint
  - Validates Azure authentication configuration

**Prerequisites:**
1. Uncomment the Azure Key Vault dependency in `pom.xml`
2. Ensure the certificate exists at `~/.azure/certs/investpulse-net-infra-full.pem`
3. Service Principal must have access to the Key Vault
4. Secret `twitter-bearer-token` must exist in Azure Key Vault

**Run the integration test:**
```bash
# Enable the integration test with environment variable
AZURE_KEYVAULT_TEST_ENABLED=true mvn test -Dtest=AzureKeyVaultIntegrationTest
```

**Note:** This test is disabled by default (skipped) to avoid failures when Azure Key Vault is not available or the dependency is commented out.

## Usage

Once the Azure Key Vault integration is enabled, client applications (like the X/Twitter service) can retrieve the configuration:

```bash
# Get configuration for 'x' application
curl http://localhost:8888/x/default
```

The response will include the `twitter.bearer.token` property with the value retrieved from Azure Key Vault.

## Local Development

For local development without Azure Key Vault access, you can:

1. Use the test properties that include a mock token
2. Override the property in your local `application.properties`:
   ```properties
   twitter-bearer-token=your-local-development-token
   ```
3. Set an environment variable:
   ```bash
   export TWITTER_BEARER_TOKEN=your-local-development-token
   ```

## Future Work

- Update to a compatible version of Azure Spring Cloud when available
- Add support for additional secrets from Azure Key Vault
- Implement secret rotation handling
- Add monitoring and alerts for Key Vault access failures
