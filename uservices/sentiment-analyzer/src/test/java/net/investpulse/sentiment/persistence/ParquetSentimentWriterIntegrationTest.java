package net.investpulse.sentiment.persistence;

import net.investpulse.common.dto.SentimentResult;
import net.investpulse.sentiment.schema.SentimentResultSchema;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.generic.GenericDatumReader;
import org.apache.avro.generic.GenericRecord;
import org.apache.hadoop.fs.Path;
import org.apache.parquet.avro.AvroParquetReader;
import org.apache.parquet.hadoop.ParquetReader;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.File;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration test for {@link ParquetSentimentWriter} verifying end-to-end
 * Parquet file creation, partitioning structure, and data correctness.
 * 
 * <p><strong>Note:</strong> These tests are disabled due to Hadoop + Java 25 compatibility issues
 * with javax.security.auth.Subject. In production, the service runs with JVM arguments:
 * <pre>--enable-native-access=ALL-UNNAMED --add-opens java.base/javax.security.auth=ALL-UNNAMED</pre>
 * 
 * <p>Tests validate:
 * <ul>
 *   <li>Spark-compatible partition directory structure</li>
 *   <li>Parquet file creation with Snappy compression</li>
 *   <li>Avro schema correctness</li>
 *   <li>Data serialization/deserialization accuracy</li>
 *   <li>File rotation based on record count threshold</li>
 * </ul>
 */
@Disabled("Hadoop compatibility with Java 25 requires runtime JVM flags not available in Surefire")
class ParquetSentimentWriterIntegrationTest {

    @TempDir
    File tempDir;

    private ParquetSentimentWriter writer;
    private SentimentResultSchema schema;

    @BeforeEach
    void setUp() {
        schema = new SentimentResultSchema();
        writer = new ParquetSentimentWriter(schema);
        
        // Override base path to use temp directory
        ReflectionTestUtils.setField(writer, "basePath", tempDir.getAbsolutePath());
        ReflectionTestUtils.setField(writer, "maxRecordsPerFile", 3); // Small for testing rotation
        ReflectionTestUtils.setField(writer, "queueCapacity", 1000);
        
        // Manually initialize since @PostConstruct isn't called in unit tests
        writer.init();
    }

    @AfterEach
    void tearDown() {
        writer.shutdown();
    }

    @Test
    void shouldCreatePartitionedParquetFiles() throws ExecutionException, InterruptedException, IOException {
        // Given
        var now = Instant.now();
        var result = new SentimentResult(
            "tweet123",
            "AAPL",
            0.75,
            "POSITIVE",
            now,
            "@ZeroHedge",
            "X API"
        );

        // When
        writer.writeAsync(result).get();
        writer.shutdown(); // Force file close

        // Then
        var date = LocalDate.ofInstant(now, ZoneOffset.UTC);
        var expectedPartitionPath = String.format(
            "%s/ticker=AAPL/year=%d/month=%02d/day=%02d",
            tempDir.getAbsolutePath(),
            date.getYear(),
            date.getMonthValue(),
            date.getDayOfMonth()
        );

        var partitionDir = new File(expectedPartitionPath);
        assertTrue(partitionDir.exists(), "Partition directory should exist: " + expectedPartitionPath);
        assertTrue(partitionDir.isDirectory(), "Should be a directory");

        var files = partitionDir.listFiles((dir, name) -> name.endsWith(".parquet"));
        assertNotNull(files, "Should have files in partition directory");
        assertEquals(1, files.length, "Should have exactly one Parquet file");
    }

    @Test
    void shouldWriteCorrectDataToParquet() throws ExecutionException, InterruptedException, IOException {
        // Given
        var now = Instant.parse("2025-12-26T10:15:30.00Z");
        var result = new SentimentResult(
            "tweet456",
            "TSLA",
            -0.45,
            "NEGATIVE",
            now,
            "@TechAnalyst",
            "X API"
        );

        // When
        writer.writeAsync(result).get();
        writer.shutdown();

        // Then
        var parquetFile = findParquetFile("TSLA", now);
        assertNotNull(parquetFile, "Parquet file should exist");

        var records = readParquetFile(parquetFile);
        assertEquals(1, records.size(), "Should have one record");

        var record = records.get(0);
        assertEquals("tweet456", record.get("tweetId").toString());
        assertEquals("TSLA", record.get("ticker").toString());
        assertEquals(-0.45, (Double) record.get("score"), 0.001);
        assertEquals("NEGATIVE", record.get("sentiment").toString());
        assertEquals(now.toEpochMilli(), record.get("processedAt"));
        assertEquals("@TechAnalyst", record.get("publisher").toString());
        assertEquals("X API", record.get("source").toString());
    }

    @Test
    void shouldRotateFilesAfterThreshold() throws ExecutionException, InterruptedException {
        // Given: maxRecordsPerFile set to 3 in setUp
        var results = List.of(
            createTestResult("tweet1", "AAPL", Instant.now()),
            createTestResult("tweet2", "AAPL", Instant.now()),
            createTestResult("tweet3", "AAPL", Instant.now()),
            createTestResult("tweet4", "AAPL", Instant.now()) // Should trigger rotation
        );

        // When
        for (var result : results) {
            writer.writeAsync(result).get();
        }
        writer.shutdown();

        // Then
        var date = LocalDate.now(ZoneOffset.UTC);
        var partitionPath = String.format(
            "%s/ticker=AAPL/year=%d/month=%02d/day=%02d",
            tempDir.getAbsolutePath(),
            date.getYear(),
            date.getMonthValue(),
            date.getDayOfMonth()
        );

        var partitionDir = new File(partitionPath);
        var files = partitionDir.listFiles((dir, name) -> name.endsWith(".parquet"));
        assertNotNull(files);
        assertTrue(files.length >= 2, "Should have rotated to at least 2 files, got: " + files.length);
    }

    @Test
    void shouldDropRecordWhenQueueFull() throws ExecutionException, InterruptedException {
        // Given: Set very small queue capacity
        ReflectionTestUtils.setField(writer, "queueCapacity", 2);
        
        // When: Attempt to write more records than queue capacity
        var futures = new ArrayList<java.util.concurrent.CompletableFuture<Void>>();
        for (int i = 0; i < 5; i++) {
            var future = writer.writeAsync(createTestResult("tweet" + i, "AAPL", Instant.now()));
            futures.add(future);
        }

        // Then: Some futures should complete with exceptions (dropped records)
        var droppedCount = futures.stream()
            .filter(f -> {
                try {
                    f.get();
                    return false;
                } catch (Exception e) {
                    return true;
                }
            })
            .count();

        assertTrue(droppedCount > 0, "Should have dropped at least one record");
    }

    private SentimentResult createTestResult(String tweetId, String ticker, Instant timestamp) {
        return new SentimentResult(
            tweetId,
            ticker,
            0.5,
            "NEUTRAL",
            timestamp,
            "@TestPublisher",
            "X API"
        );
    }

    private File findParquetFile(String ticker, Instant timestamp) {
        var date = LocalDate.ofInstant(timestamp, ZoneOffset.UTC);
        var partitionPath = String.format(
            "%s/ticker=%s/year=%d/month=%02d/day=%02d",
            tempDir.getAbsolutePath(),
            ticker,
            date.getYear(),
            date.getMonthValue(),
            date.getDayOfMonth()
        );

        var partitionDir = new File(partitionPath);
        if (!partitionDir.exists()) {
            return null;
        }

        var files = partitionDir.listFiles((dir, name) -> name.endsWith(".parquet"));
        return (files != null && files.length > 0) ? files[0] : null;
    }

    private List<GenericRecord> readParquetFile(File parquetFile) throws IOException {
        var records = new ArrayList<GenericRecord>();
        var path = new Path(parquetFile.getAbsolutePath());

        try (ParquetReader<GenericRecord> reader = AvroParquetReader
                .<GenericRecord>builder(path)
                .build()) {
            GenericRecord record;
            while ((record = reader.read()) != null) {
                records.add(record);
            }
        }

        return records;
    }
}
