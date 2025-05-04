package onlexnet.webapi.edgar;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@ContextConfiguration(classes = EdgarConfig.class)
public class EdgarApiTest {

  @Autowired
  PooledEdgarApi sut;

  @Test
  void shouldDownloadTickers() {
    var response = sut.exec(it -> it.getTickers());
    Assertions.assertThat(response).isNotEmpty();
  }

  @Test
  void shouldDownloadDocsIndex() {
    // https://data.sec.gov/submissions/CIK0000789019.json
    var response = sut.exec(it -> it.getSubmissions("0000789019"));
    Assertions.assertThat(response).isNotNull();
  }

}
