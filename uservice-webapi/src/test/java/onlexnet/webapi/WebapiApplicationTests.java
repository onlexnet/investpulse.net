package onlexnet.webapi;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.kafka.KafkaContainer;

@Testcontainers
@SpringBootTest
class WebapiApplicationTests {

  @Container
  @ServiceConnection
  static KafkaContainer kafka = new KafkaContainer("apache/kafka-native:3.8.0");

	@Test
	void contextLoads() {
	}

}
