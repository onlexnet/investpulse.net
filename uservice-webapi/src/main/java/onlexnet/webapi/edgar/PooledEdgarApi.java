package onlexnet.webapi.edgar;

import org.springframework.stereotype.Component;

/**
 * https://www.sec.gov/about/webmaster-frequently-asked-questions#developers
 */
@Component
public class PooledEdgarApi extends PooledExecutor<EdgarApi> {
  private PooledEdgarApi(EdgarApi it) {
    super(it);
  }

  static PooledEdgarApi started(EdgarApi it) {
    var result = new PooledEdgarApi(it);
    result.startAsync();
    return result;
  }

}
