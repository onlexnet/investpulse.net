package onlexnet.webapi.edgar;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.util.Assert;
import org.springframework.web.client.RestClient;

import lombok.RequiredArgsConstructor;

/**
 * Sends requests to Edgar api making sure no more that 10 req/sec is sent.
 * Is is required by Edgar as part of fair use
 * https://www.sec.gov/search-filings/edgar-application-programming-interfaces
 */
public interface EdgarApi {

  record CompanyTicker(long cik_str, String ticker, String title) {
  }

  // https://www.sec.gov/files/company_tickers.json
  Map<String, CompanyTicker> getTickers();

  
  public record EdgarSubmission(
    String cik,
    String entityType,
    String sic,
    String sicDescription,
    boolean insiderTransactionForOwnerExists,
    boolean insiderTransactionForIssuerExists,
    String name,
    List<String> tickers,
    List<String> exchanges,
    String ein,
    String description,
    String website,
    Filings filings
) {
    public EdgarSubmission {
        Objects.requireNonNull(cik, "CIK cannot be null");
        Objects.requireNonNull(entityType, "Entity type cannot be null");
        Objects.requireNonNull(name, "Company name cannot be null");
        Objects.requireNonNull(filings, "Filings cannot be null");

        if (cik.isBlank()) throw new IllegalArgumentException("CIK cannot be blank");
        if (name.isBlank()) throw new IllegalArgumentException("Company name cannot be blank");
    }

    public record Filings(Recent recent) {
        public Filings {
            Objects.requireNonNull(recent, "Recent filings cannot be null");
        }
    }

    public record Recent(
        List<String> accessionNumber,
        List<LocalDate> filingDate,
        List<LocalDate> reportDate,
        List<LocalDateTime> acceptanceDateTime,
        List<String> act,
        List<String> form,
        List<String> fileNumber,
        List<String> filmNumber,
        List<String> items,
        List<Integer> size,
        List<Boolean> isXBRL,
        List<Boolean> isInlineXBRL,
        List<String> primaryDocument,
        List<String> primaryDocDescription
    ) {
        public Recent {
            Objects.requireNonNull(accessionNumber, "Accession numbers cannot be null");
            Objects.requireNonNull(filingDate, "Filing dates cannot be null");
            Objects.requireNonNull(reportDate, "Report dates cannot be null");
            Objects.requireNonNull(form, "Form types cannot be null");

            if (accessionNumber.isEmpty()) throw new IllegalArgumentException("At least one accession number is required");
            if (filingDate.isEmpty()) throw new IllegalArgumentException("At least one filing date is required");
            if (form.isEmpty()) throw new IllegalArgumentException("At least one form type is required");
        }
    }
}
  EdgarSubmission getSubmissions(String cik);
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

  @Override
  public EdgarSubmission getSubmissions(String cik) {
    Assert.isTrue(cik.length() == 10, "'cik' is the entity's 10-digit central index key (CIK), including leading zeros.");
    var result = restClient.get()
        .uri("https://data.sec.gov/submissions/CIK{cik}.json", cik)
        .retrieve()
        .body(EdgarSubmission.class);

    var fillings = result.filings().recent();
    for (var i = 0; i < fillings.form().size(); i++) {
      if (!fillings.form().get(i).equals("10-K")) {
        fillings.form().remove(i);
        fillings.filingDate().remove(i);
        fillings.reportDate().remove(i);
        fillings.accessionNumber().remove(i);
        i--;
      }
    }
    Assert.isTrue(fillings.form().size() > 0, "test");

    return result;
  }

}
