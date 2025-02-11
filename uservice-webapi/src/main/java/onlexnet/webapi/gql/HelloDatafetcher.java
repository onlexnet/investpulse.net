package onlexnet.webapi.gql;

import com.netflix.graphql.dgs.DgsComponent;
import com.netflix.graphql.dgs.DgsQuery;

import graphql.schema.DataFetchingEnvironment;
import onlexnet.webapi.codegen.types.Hello;

@DgsComponent
public class HelloDatafetcher {

  @DgsQuery
  public Hello hello(DataFetchingEnvironment dataFetchingEnvironment) {
    return new Hello.Builder().text("Hello world!").build();
  }
}