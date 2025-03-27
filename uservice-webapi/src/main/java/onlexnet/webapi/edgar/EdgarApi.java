package onlexnet.webapi.edgar;

import java.util.List;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import lombok.RequiredArgsConstructor;

/**
 * Sends requests to Edgar api making sure no more that 10 req/sec is sent.
 * Is is required by Edgar as part of fair use
 * https://www.sec.gov/about/webmaster-frequently-asked-questions#developers
 */
public interface EdgarApi {
  
  record CompanyTicker() { }

  // https://www.sec.gov/files/company_tickers.json
  List<CompanyTicker> getTickers();
}

@Component
@RequiredArgsConstructor
class EdgarApiCttpClient implements EdgarApi {

  // We use single instance as it is thread safe
  // https://docs.spring.io/spring-framework/reference/integration/rest-clients.html#_creating_a_restclient
  private final RestClient restClient;


  ParameterizedTypeReference<List<CompanyTicker>> listOfCompanyTickers = new ParameterizedTypeReference<List<CompanyTicker>>() { };

  @Override
  public List<CompanyTicker> getTickers() {
    var result = restClient.get().accept(MediaType.APPLICATION_JSON).retrieve().body(listOfCompanyTickers);
    return result;
  }

  
}
