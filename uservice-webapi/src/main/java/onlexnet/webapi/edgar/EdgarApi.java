package onlexnet.webapi.edgar;

import java.util.List;
import java.util.Map;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.http.HttpHeaders;
import lombok.RequiredArgsConstructor;

/**
 * Sends requests to Edgar api making sure no more that 10 req/sec is sent.
 * Is is required by Edgar as part of fair use
 * https://www.sec.gov/about/webmaster-frequently-asked-questions#developers
 */
public interface EdgarApi {

  record CompanyTicker(long cik_str, String ticker, String title) {
  }

  // https://www.sec.gov/files/company_tickers.json
  Map<String, CompanyTicker> getTickers();
}

@Component
@RequiredArgsConstructor
class EdgarApiHttpClient implements EdgarApi {

  // We use single instance as it is thread safe
  // https://docs.spring.io/spring-framework/reference/integration/rest-clients.html#_creating_a_restclient
  private final RestClient restClient;

  ParameterizedTypeReference<Map<String, CompanyTicker>> listOfCompanyTickers = new ParameterizedTypeReference<>() {
  };

  @Override
  public Map<String, CompanyTicker> getTickers() {
    return restClient.get()
        .uri("https://www.sec.gov/files/company_tickers.json")
        .retrieve()
        .body(listOfCompanyTickers);
  }

}
