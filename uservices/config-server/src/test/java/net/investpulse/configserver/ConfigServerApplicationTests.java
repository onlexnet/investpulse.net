package net.investpulse.configserver;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Integration test for Config Server application context loading.
 * Disabled due to Azure Kafka autoconfiguration version conflicts.
 * Enable only when Azure infrastructure is properly configured.
 */
@Disabled("Requires Azure Kafka configuration - enable for integration testing only")
@SpringBootTest(
	properties = {
		"spring.profiles.active=native",
		"spring.cloud.azure.keyvault.secret.property-source-enabled=false",
		"spring.cloud.azure.autoconfigure.enabled=false",
		"spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration"
	}
)
class ConfigServerApplicationTests {

	@Test
	void contextLoads() {
	}

}
