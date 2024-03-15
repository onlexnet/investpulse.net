package onlexnet.demo;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import onlexnet.market.events.MarketChangedEvent;

@Slf4j
public class MyTest {
    
    @Test
    @SneakyThrows
    void test1() {
        var json = "{ \"date\": 20010203}";
        var mapper = new ObjectMapper();
        var actual = mapper.readValue(json, MarketChangedEvent.class);

        var expected = new MarketChangedEvent(20010203L);

        Assertions.assertThat(actual).isEqualTo(expected);
        
    }
}
