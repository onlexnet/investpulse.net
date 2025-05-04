package onlexnet.webapi.edgar;

import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

/**
 * https://www.sec.gov/about/webmaster-frequently-asked-questions#developers
 */
@Component
public class PooledEdgarApi extends PooledExecutor<EdgarApi> {
  private PooledEdgarApi(EdgarApi it, EdgarHttpPolicy policy) {
    super(it, policy);
  }

  @Bean
  PooledEdgarApi started(EdgarApi it, EdgarHttpPolicy policy) {
    var result = new PooledEdgarApi(it, policy);
    result.startAsync();
    return result;
  }

}
