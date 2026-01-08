package net.investpulse.sentiment.config;

import com.fasterxml.jackson.databind.Module;
import com.fasterxml.jackson.databind.module.SimpleModule;
import net.investpulse.common.config.InstantDeserializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.time.Instant;

/**
 * Jackson configuration for custom deserializers.
 * Registers the InstantDeserializer for handling Reddit timestamp formats.
 */
@Configuration
public class JacksonConfiguration {
    
    @Bean
    public Module customInstantModule() {
        SimpleModule module = new SimpleModule();
        module.addDeserializer(Instant.class, new InstantDeserializer());
        return module;
    }
}
