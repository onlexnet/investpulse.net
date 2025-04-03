package onlexnet.webapi.edgar;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
class EdgarConfigurer {
  
  @Bean
  RestClient restClient() {
    return RestClient
        .builder()
        .defaultHeader("User-Agent", "OnLex.net slawomir.siudek@onlex.net")
        .defaultHeader("Host", "www.sec.gov")
        .build();
  }
}
