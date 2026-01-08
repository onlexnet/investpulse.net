package net.investpulse.common.config;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import java.io.IOException;
import java.time.Instant;

/**
 * Custom Jackson deserializer for java.time.Instant fields.
 * Handles both:
 * - Epoch milliseconds (long): 1767817028120
 * - Epoch seconds with nanoseconds (double): 1767817028.120290979
 *
 * Useful for deserializing Reddit messages that may use seconds.nanos format.
 */
public class InstantDeserializer extends JsonDeserializer<Instant> {
    @Override
    public Instant deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        long epochMillis;
        
        if (p.currentToken().isNumeric()) {
            double value = p.getDoubleValue();
            
            // If value > 1e11, it's already in milliseconds (about year 5138)
            // Otherwise, assume it's in seconds (from epoch to year 5138)
            if (value > 1e11) {
                epochMillis = (long) value;
            } else {
                // Convert from seconds to milliseconds
                epochMillis = Math.round(value * 1000);
            }
        } else {
            // Fall back to string parsing (ISO-8601)
            String text = p.getText();
            return Instant.parse(text);
        }
        
        return Instant.ofEpochMilli(epochMillis);
    }
}
