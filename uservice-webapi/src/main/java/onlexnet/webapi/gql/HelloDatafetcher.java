package onlexnet.webapi.gql;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsQuery;

import graphql.schema.DataFetchingEnvironment;
import onlexnet.webapi.edgar.EdgarApi;

@DgsComponent
public class HelloDatafetcher {

  private final EdgarApi edgarApi;

  public HelloDatafetcher(EdgarApi edgarApi) {
    this.edgarApi = edgarApi;
  }

  @DgsQuery
  public Hello hello(DataFetchingEnvironment dataFetchingEnvironment) {
    var tickers = edgarApi.getTickers();
    var result = new Hello(tickers.size());
    return result;
  }

  public record Hello(int count) { }
}

