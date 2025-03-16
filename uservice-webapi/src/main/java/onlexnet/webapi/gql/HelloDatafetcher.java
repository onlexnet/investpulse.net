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
    return new Hello().setText("Hello world!");
  }
}

@Data
@Accessors(chain = true)
class Hello {
  String text;
}