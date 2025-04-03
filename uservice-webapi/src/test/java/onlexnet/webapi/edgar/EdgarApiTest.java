package onlexnet.webapi.edgar;

import java.util.Map;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.web.client.RestClient;

import onlexnet.webapi.edgar.EdgarApi.CompanyTicker;

@ExtendWith(SpringExtension.class)
@ContextConfiguration(classes = EdgarConfig.class)
public class EdgarApiTest {

  @Autowired
  EdgarApi edgarApi;

  @Test
  void shouldDownloadTickers() {
    var response = edgarApi.getTickers();
    Assertions.assertThat(response).isNotEmpty();
  }

}
