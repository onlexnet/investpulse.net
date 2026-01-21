package net.investpulse.sentiment.persistence;

import java.io.IOException;
import java.util.HashMap;

import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.api.WriteSupport;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.apache.parquet.io.OutputFile;
import org.apache.parquet.io.api.Binary;
import org.apache.parquet.io.api.RecordConsumer;
import org.apache.parquet.schema.MessageType;

import net.investpulse.common.dto.SentimentResult;

/**
 * Builder for creating {@link ParquetWriter} instances for {@link SentimentResult} records.
 * Uses direct {@link LocalOutputFile} to bypass Hadoop security framework.
 */
public class SentimentResultParquetWriter {

    public static ParquetWriter<SentimentResult> builder(OutputFile file, MessageType schema,
                                                         CompressionCodecName compression,
                                                         int rowGroupSize, int pageSize) throws IOException {
        var builder = new CustomBuilder(file, schema);
        return builder
            .withCompressionCodec(compression)
            .withRowGroupSize(rowGroupSize)
            .withPageSize(pageSize)
            .build();
    }

    /**
     * Custom builder that uses our WriteSupport implementation.
     */
    private static class CustomBuilder extends ParquetWriter.Builder<SentimentResult, CustomBuilder> {
        private final MessageType schema;

        protected CustomBuilder(OutputFile file, MessageType schema) {
            super(file);
            this.schema = schema;
        }

        @Override
        protected CustomBuilder self() {
            return this;
        }

        @Override
        protected WriteSupport<SentimentResult> getWriteSupport(org.apache.hadoop.conf.Configuration conf) {
            return new SentimentResultWriteSupport(schema);
        }
    }

    /**
     * Implements {@link WriteSupport} for {@link SentimentResult} records.
     */
    private static class SentimentResultWriteSupport extends WriteSupport<SentimentResult> {
        private final MessageType schema;
        private RecordConsumer recordConsumer;

        SentimentResultWriteSupport(MessageType schema) {
            this.schema = schema;
        }

        @Override
        public WriteContext init(org.apache.hadoop.conf.Configuration configuration) {
            return new WriteContext(schema, new HashMap<>());
        }

        @Override
        public void prepareForWrite(RecordConsumer recordConsumer) {
            this.recordConsumer = recordConsumer;
        }

        @Override
        public void write(SentimentResult record) {
            recordConsumer.startMessage();
            
            // tweetId
            recordConsumer.startField("tweetId", 0);
            recordConsumer.addBinary(Binary.fromString(record.tweetId()));
            recordConsumer.endField("tweetId", 0);
            
            // ticker
            recordConsumer.startField("ticker", 1);
            recordConsumer.addBinary(Binary.fromString(record.ticker()));
            recordConsumer.endField("ticker", 1);
            
            // score
            recordConsumer.startField("score", 2);
            recordConsumer.addDouble(record.score());
            recordConsumer.endField("score", 2);
            
            // sentiment
            recordConsumer.startField("sentiment", 3);
            recordConsumer.addBinary(Binary.fromString(record.sentiment()));
            recordConsumer.endField("sentiment", 3);
            
            // processedAt (timestamp as epoch millis)
            recordConsumer.startField("processedAt", 4);
            recordConsumer.addLong(record.processedAt().toEpochMilli());
            recordConsumer.endField("processedAt", 4);
            
            // publisher
            recordConsumer.startField("publisher", 5);
            recordConsumer.addBinary(Binary.fromString(record.publisher()));
            recordConsumer.endField("publisher", 5);
            
            // source
            recordConsumer.startField("source", 6);
            recordConsumer.addBinary(Binary.fromString(record.source()));
            recordConsumer.endField("source", 6);
            
            // originalTimestamp (timestamp as epoch millis)
            recordConsumer.startField("originalTimestamp", 7);
            recordConsumer.addLong(record.originalTimestamp().toEpochMilli());
            recordConsumer.endField("originalTimestamp", 7);
            
            recordConsumer.endMessage();
        }
    }
}
