package onlexnet.agent.app;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.modulith.test.ApplicationModuleTest;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.SneakyThrows;
import onlexnet.pdt.bank.events.BankAccountStateChanged;

@ApplicationModuleTest
public class AvroDeSerTest {

    @Autowired
    ObjectMapper objectMapper;

    @Test
    @SneakyThrows
    public void shoulDeSer() {
        var expected = new BankAccountStateChanged("app", 2_000d);
        var eventAsString = objectMapper.writeValueAsString(expected);
        var actual = objectMapper.readValue(eventAsString, expected.getClass());

        Assertions.assertThat(actual).isEqualTo(expected);
    }
}
