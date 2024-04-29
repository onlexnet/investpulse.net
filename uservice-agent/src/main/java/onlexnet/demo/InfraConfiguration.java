package onlexnet.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.fasterxml.jackson.databind.ObjectMapper;

@Configuration
class InfraConfiguration {
    
    @Bean
    ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
