package net.investpulse.sentiment.schema;

import net.investpulse.common.dto.SentimentResult;
import org.apache.avro.Schema;
import org.apache.avro.SchemaBuilder;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.springframework.stereotype.Component;

/**
 * Defines the Avro schema for {@link SentimentResult} records and provides
 * conversion utilities for Parquet persistence.
 * 
 * <p>The schema maps Java Records to Avro GenericRecords for columnar storage:
 * <ul>
 *   <li>{@link java.time.Instant} fields are stored as epoch milliseconds (long)</li>
 *   <li>All other fields maintain their native types (String, double)</li>
 * </ul>
 */
@Component
public class SentimentResultSchema {

    private static final String NAMESPACE = "net.investpulse.common.dto";
    private static final String RECORD_NAME = "SentimentResult";
    
    private final Schema schema;

    public SentimentResultSchema() {
        this.schema = SchemaBuilder.record(RECORD_NAME)
            .namespace(NAMESPACE)
            .fields()
            .requiredString("tweetId")
            .requiredString("ticker")
            .requiredDouble("score")
            .requiredString("sentiment")
            .name("processedAt").type().longType().noDefault() // Instant → epoch millis
            .requiredString("publisher")
            .requiredString("source")
            .endRecord();
    }

    /**
     * Returns the Avro schema for SentimentResult.
     * 
     * @return immutable Avro schema instance
     */
    public Schema getSchema() {
        return schema;
    }

    /**
     * Converts a {@link SentimentResult} Java Record to an Avro GenericRecord
     * for Parquet serialization.
     * 
     * <p>Instant timestamps are converted to epoch milliseconds, losing
     * nanosecond precision. This is acceptable for analytics use cases.
     * 
     * @param result the sentiment analysis result to convert
     * @return Avro GenericRecord ready for Parquet writing
     */
    public GenericRecord toAvroRecord(SentimentResult result) {
        var record = new GenericData.Record(schema);
        record.put("tweetId", result.tweetId());
        record.put("ticker", result.ticker());
        record.put("score", result.score());
        record.put("sentiment", result.sentiment());
        record.put("processedAt", result.processedAt().toEpochMilli());
        record.put("publisher", result.publisher());
        record.put("source", result.source());
        return record;
    }
}
