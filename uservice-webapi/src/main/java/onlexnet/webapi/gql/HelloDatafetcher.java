package onlexnet.webapi.gql;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsQuery;

import graphql.schema.DataFetchingEnvironment;
import lombok.Data;
import lombok.experimental.Accessors;

@DgsComponent
public class HelloDatafetcher {

  @DgsQuery
  public Hello hello(DataFetchingEnvironment dataFetchingEnvironment) {
    var result = new Hello();
    result.setText("Hello world!");
    return result;
  }

  @Data
  public static class Hello {
    private String text;
  }
}

