package net.investpulse.sentiment.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.AsyncTaskExecutor;
import org.springframework.core.task.VirtualThreadTaskExecutor;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Configuration for virtual thread support in sentiment-analyzer.
 * Virtual threads enable lightweight concurrency with less memory overhead.
 * This configuration is only applied when spring.threads.virtual.enabled=true.
 */
@Slf4j
@Configuration
@EnableAsync
@ConditionalOnProperty(name = "spring.threads.virtual.enabled", havingValue = "true")
public class VirtualThreadConfiguration {

    /**
     * Configures async processing to use virtual threads.
     * Virtual threads provide superior scalability for I/O-bound operations
     * like Kafka consumption and Parquet file writes.
     *
     * @return AsyncTaskExecutor using virtual threads
     */
    @Bean(name = "taskExecutor")
    public AsyncTaskExecutor asyncTaskExecutor() {
        log.info("Initializing virtual thread task executor for sentiment-analyzer");
        return new VirtualThreadTaskExecutor("sentiment-analyzer-vthread-");
    }
}
