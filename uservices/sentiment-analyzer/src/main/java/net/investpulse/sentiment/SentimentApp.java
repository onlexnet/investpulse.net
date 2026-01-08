package net.investpulse.sentiment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Sentiment Analyzer microservice for financial sentiment analysis.
 * 
 * <p>Consumes raw tweets from {@code ticker-*} topics, performs NLP sentiment
 * scoring, and publishes results to both Kafka and Parquet files for analytics.
 * 
 * <p><strong>Key Features:</strong>
 * <ul>
 *   <li>Async Parquet persistence with drop-and-log queue policy</li>
 *   <li>Manual Kafka offset commits after successful file writes</li>
 *   <li>Spark-optimized partitioned file structure</li>
 * </ul>
 */
@SpringBootApplication
@EnableAsync // Required for ParquetSentimentWriter.writeAsync()
@EnableScheduling // For future scheduled file rotation/cleanup tasks
public class SentimentApp {
    public static void main(String[] args) {
        SpringApplication.run(SentimentApp.class, args);
    }
}
