package onlexnet.demo;

import org.apache.avro.specific.SpecificRecord;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hubspot.jackson.datatype.protobuf.ProtobufModule;

import onlexnet.demo.DaprCallback.JacksonIgnoreAvroPropertiesMixIn;

@Configuration
class InfraConfiguration {

    @Bean
    ObjectMapper objectMapper() {

        var bean = new ObjectMapper();
        bean.registerModule(new ProtobufModule());

        bean.addMixIn(SpecificRecord.class, // Interface implemented by all generated Avro-Classes
                JacksonIgnoreAvroPropertiesMixIn.class);

        return bean;
    }
}
