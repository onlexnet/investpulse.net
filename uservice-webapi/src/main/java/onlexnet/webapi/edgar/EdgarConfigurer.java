package onlexnet.webapi.edgar;

import java.net.http.HttpClient;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
class EdgarConfigurer {
  
  @Bean
  RestClient restClient() {
    return RestClient.create();
  }
}
