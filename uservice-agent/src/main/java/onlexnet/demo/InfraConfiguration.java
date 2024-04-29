package onlexnet.demo;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hubspot.jackson.datatype.protobuf.ProtobufModule;

@Configuration
class InfraConfiguration {

    @Bean
    ObjectMapper objectMapper() {

        var mapper = new ObjectMapper();
        mapper.registerModule(new ProtobufModule());
        return mapper;
    }
}
